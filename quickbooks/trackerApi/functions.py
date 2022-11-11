from django.db import models
from django.db.models import Func

"""
Epoch function
Usage: posts.annotate(response_time_sec=Epoch(F('end_date') - F('start_date')))
"""
class Epoch(Func):
    template = 'EXTRACT(epoch FROM %(expressions)s)'
    output_field = models.IntegerField()

"""
Sum(Round(Epoch)) function
"""
class SumRoundEpoch(Func):
    template = 'SUM(round(((EXTRACT(epoch FROM %(expressions)s) / %(param)s), 2)'
    output_field = models.IntegerField()

    def __init__(self, expression, param, **extra):
        output_field = models.IntegerField()

        super(SumRoundEpoch, self).__init__(expression, param=param, output_field=output_field, **extra)


"""
Get distance of two points
"""
def distance(loc1, loc2):
    data = hs.haversine(loc1,loc2, unit=Unit.MILES)
    return data
