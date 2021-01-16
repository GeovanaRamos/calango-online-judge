import json
import requests
import re
from django.utils import timezone
from judge import models


def submit_to_judge_service(code, question_pk, submission):
    test_cases = models.TestCase.objects.filter(question__pk=question_pk)

    cases = []
    for case in test_cases:
        cases.append(
            {"input": re.split('\s*\\n\s*', case.inputs), "output": case.output}
        )

    data = {
        "code": code,
        "cases": cases,
    }

    # TODO pass url to settings
    r = requests.post("http://localhost:8080/judge", data=json.dumps(data),
                      headers={'content-type': 'application/json'})
    print(r.json())
    result_json = r.json()
    submission.result = result_json['message']
    submission.judged_at = timezone.localtime()
    submission.save()

