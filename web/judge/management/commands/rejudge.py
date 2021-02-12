import sys

from django.core.management import BaseCommand
from django.db import transaction

from judge.models import Submission
from judge.tasks import submit_to_judge_service


class Command(BaseCommand):
    help = 'Rejudge submissions.'

    def add_arguments(self, parser):
        # optional
        parser.add_argument('--from-pk', type=int, help='Defines from which submission to begin.')
        parser.add_argument('--to-pk', type=int, help='Defines which submission to stop.')

    @transaction.atomic
    def handle(self, *args, **kwargs):
        from_pk = kwargs['from_pk']
        to_pk = kwargs['to_pk']

        if from_pk is None or to_pk is None:
            self.stdout.write(self.style.ERROR("No FROM or TO values."))
            sys.exit()

        if from_pk > to_pk:
            self.stdout.write(self.style.ERROR("FROM must be greater than TO."))
            sys.exit()

        submissions = Submission.objects.filter(pk__range=(from_pk, to_pk))

        if not submissions.exists():
            self.stdout.write(self.style.ERROR("No submissions"))
            sys.exit()

        for submission in submissions:
            log = submission.result
            submit_to_judge_service(submission.code, submission.question.pk, submission)
            if log != submission.result:
                self.stdout.write(
                    self.style.WARNING("ID=" + str(submission.pk) + ": " + log + " to " + submission.result))
            else:
                self.stdout.write("ID=" + str(submission.pk))
