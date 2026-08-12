from django.db import models
from apps.common.models.base import BaseModel

class MasterEntity(BaseModel):
    code = models.CharField(max_length=50, unique=True, db_index=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        abstract = True
        ordering = ['display_order', 'name']

    def __str__(self):
        return f"{self.name} ({self.code})"

class CaseType(MasterEntity): pass
class CaseCategory(MasterEntity): pass
class Court(MasterEntity): pass
class CourtLevel(MasterEntity): pass
class HearingType(MasterEntity): pass
class CasePriority(MasterEntity): pass
class CaseStage(MasterEntity): pass
class CaseStatus(MasterEntity): pass

class Act(MasterEntity): pass
class Section(MasterEntity):
    act = models.ForeignKey(Act, on_delete=models.CASCADE, related_name='sections')

class Country(MasterEntity): pass
class State(MasterEntity):
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='states')

class District(MasterEntity):
    state = models.ForeignKey(State, on_delete=models.CASCADE, related_name='districts')

class PoliceStation(MasterEntity):
    district = models.ForeignKey(District, on_delete=models.CASCADE, related_name='police_stations')

class Currency(MasterEntity): pass
class TaskTemplate(MasterEntity): pass

class CourtRoom(BaseModel):
    court = models.ForeignKey(Court, on_delete=models.CASCADE, related_name='court_rooms')
    room_number = models.CharField(max_length=50)
    floor = models.CharField(max_length=50, blank=True)
    capacity = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('court', 'room_number')

    def __str__(self):
        return f"{self.court.name} - Room {self.room_number}"

class CourtHoliday(BaseModel):
    court = models.ForeignKey(Court, on_delete=models.CASCADE, related_name='holidays')
    date = models.DateField()
    description = models.CharField(max_length=255)
    is_recurring_yearly = models.BooleanField(default=False)

    class Meta:
        unique_together = ('court', 'date')

    def __str__(self):
        return f"{self.court.name} - {self.date} ({self.description})"
