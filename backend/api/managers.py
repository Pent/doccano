from django.conf import settings
from django.db.models import Count, Manager


class AnnotationManager(Manager):

    def calc_label_distribution(self, examples, users, labels):
        """Calculate label distribution.

        Args:
            examples: example queryset.
            users: user queryset.
            labels: label queryset.

        Returns:
            label distribution per user.

        Examples:
            >>> self.calc_label_distribution(examples, users, labels)
            {'admin': {'positive': 10, 'negative': 5}}
        """
        distribution = {user.username: {label.text: 0 for label in labels} for user in users}
        items = self.filter(example_id__in=examples)\
            .values('user__username', 'label__text')\
            .annotate(count=Count('label__text'))
        for item in items:
            username = item['user__username']
            label = item['label__text']
            count = item['count']
            distribution[username][label] = count
        return distribution


class RoleMappingManager(Manager):

    def can_update(self, project: int, mapping_id: int, rolename: str):
        queryset = self.filter(
            project=project, role__name=settings.ROLE_PROJECT_ADMIN
        )
        if queryset.count() > 1:
            return True
        else:
            mapping = queryset.first()
            if mapping.id == mapping_id and rolename != settings.ROLE_PROJECT_ADMIN:
                return False
            return True


class ExampleManager(Manager):

    def bulk_create(self, objs, batch_size=None, ignore_conflicts=False):
        super().bulk_create(objs, batch_size=batch_size, ignore_conflicts=ignore_conflicts)
        uuids = [data.uuid for data in objs]
        examples = self.in_bulk(uuids, field_name='uuid')
        return [examples[uid] for uid in uuids]


class ExampleStateManager(Manager):

    def count_done(self, examples, user=None):
        if user:
            queryset = self.filter(example_id__in=examples, confirmed_by=user)
        else:
            queryset = self.filter(example_id__in=examples)
        return queryset.distinct().values('example').count()

    def measure_member_progress(self, examples, members):
        done_count = self.filter(example_id__in=examples)\
            .values('confirmed_by__username')\
            .annotate(total=Count('confirmed_by'))
        response = {
            'total': examples.count(),
            'progress': {
                obj['confirmed_by__username']: obj['total'] for obj in done_count
            }
        }
        for member in members:
            if member.username not in response['progress']:
                response['progress'][member.username] = 0
        return response
