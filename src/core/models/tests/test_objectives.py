from datetime import datetime, timedelta

from core.models import Board
from core.models.objectives import Habit, Due, Goal


def test_objectives():
    due = Due(datetime.now(), (datetime.now() + timedelta(days=30)))
    habit_1 = Habit(1, 'test-habit-1', due=due)
    habit_2 = Habit(2, 'test-habit-2', due=due)
    habit_3 = Habit(3, 'test-habit-3', due=due)
    habit_4 = Habit(4, 'test-habit-4', due=due)
    habit_5 = Habit(5, 'test-habit-5', due=due)
    habit_3.add_next(habit_4)
    habit_3.add_next(habit_5)
    habit_3.add_previous(habit_2)
    habit_2.add_previous(habit_1)
    assert habit_1 in habit_2.previous
    assert habit_2 in habit_1.next
    assert habit_4 in habit_3.next
    assert habit_5 in habit_3.next
    d = datetime.now()
    habit_3.set_date(d, True)
    assert d in habit_3.done_dates
    habit_3.unset_date(d)
    assert d not in habit_3.done_dates


def test_plan_map():
    due = Due(datetime.now(), (datetime.now() + timedelta(days=30)))
    goal = Goal(1, 'test-goal-1')
    habit = Habit(1, 'test-habit-1', due=due)
    goal2 = Goal(2, 'test-goal-2', due=due)
    goal.add_next(habit)
    goal2.add_previous(habit)
    plan_map = Board(1)
    plan_map.add(habit)
    plan_map.add(goal)
    plan_map.add(goal2)
    assert goal2 in habit.next
    assert habit in goal2.previous
    assert goal in habit.previous
    assert habit in goal.next
    print(plan_map.iterate())