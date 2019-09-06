import ast
import json
import logging

from botocore.exceptions import ClientError

from chalicelib.model.models import LockModel, EventModel

log = logging.getLogger(__name__)


def list_users():
    """
    Get all user IDs
    """
    user_ids = []
    for item in EventModel.scan():
        if item.user_id not in user_ids:
            user_ids.append(item.user_id)
    return json.dumps(user_ids)


def get_user(user_id):
    e = EventModel.scan(EventModel.user_id == user_id, limit=1)
    if len(e) > 0:
        return json.dumps({"message": f"{user_id} exists", "status": "OK"})
    else:
        return json.dumps({'message': f"{user_id} does not exist", "status": "NOT FOUND"})


def list_all_events():
    events = []
    for event in EventModel.scan():
        events.append(event.attribute_values)
    return json.dumps(events)


def get_all_events_by_user_id(user_id):
    events = []
    for event in EventModel.scan(EventModel.user_id == user_id):
        events.append(event.attribute_values)
    return json.dumps(events)


def     list_all_events_by_date(event_date):
    events = []
    for event in EventModel.scan(EventModel.event_date == event_date):
        events.append(event.attribute_values)
    return json.dumps(events)


def get_event_by_user_id_and_date(user_id, event_date):
    try:
        e = EventModel.get(user_id, event_date)
        return e.attribute_values
    except EventModel.DoesNotExist as e:
        return json.dumps({})


def create_event(events):
    if isinstance(events, str):
        events = ast.literal_eval(events)
    event = EventModel(
        user_id=f"{events.get('user_id')}",
        event_date=f"{events.get('event_date')}",
        user_name=f"{events.get('user_name')}",
        reason=f"{events.get('reason')}",
        hours=f"{events.get('hours')}",
    )
    return json.dumps(event.save())


def delete_event(user_id, event_date):
    """
    :param user_id:
    :param event_date:
    :return bool:
    """
    try:
        e = EventModel.get(user_id, event_date)
        return json.dumps(e.delete())
    except EventModel.DoesNotExist as e:
        return json.dumps({})


def create_lock(lock_request):
    try:
        lock = LockModel(
            hash_key=f"{lock_request.get('user_id')}",
            range_key=f"{lock_request.get('event_date')}")
        return json.dumps(lock.save())
    except ClientError as e:
        log.debug(e.response['Error']['Message'])
        return json.dumps({"error":"Failed to create lock"})


def list_all_locks():
    locks = []
    for lock in LockModel.scan():
        locks.append(lock.attribute_values)
    return json.dumps(locks)


def get_all_locks_by_date(date):
    locks = []
    for lock in LockModel.scan():
        locks.append(lock.attribute_values)
    return json.dumps(locks)


def get_lock(user_id, event_date):
    try:
        lock = LockModel.get(user_id, event_date)
        if lock:
            return lock.attribute_values
    except LockModel.DoesNotExist as e:
        return json.dumps({})


def delete_lock(user_id, event_date):
    try:
        lock = LockModel.get(user_id, event_date)
        if lock:
            return json.dumps(lock.delete())
    except LockModel.DoesNotExist as e:
        return json.dumps({})


def delete_all_locks_by_date(event_date):
    locks = LockModel.scan(LockModel.event_date == event_date)
    for lock in locks:
        lock.delete()
    return json.dumps({"Method": f"DELETE", "date": f"{event_date}", "Status": "OK"})