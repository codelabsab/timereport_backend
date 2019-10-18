import ast
import json
import logging

from botocore.exceptions import ClientError

from chalicelib.model.models import LockTable, EventTable

log = logging.getLogger(__name__)


def list_users():
    """
    returns list of all users
    """
    user_ids = []
    for item in EventTable.scan():
        if item.user_id not in user_ids:
            user_ids.append(item.user_id)
    return json.dumps(user_ids)


def get_user(user_id):
    """
    returns user_id or empty
    """
    for user in EventTable.scan(EventTable.user_id == user_id):
        return json.dumps({"message": f"{user_id} exists", "status": "OK"})
    return json.dumps({'message': f"{user_id} does not exist", "status": "NOT FOUND"})


def list_events_by_user_id(user_id):
    """
    :param user_id:
    :return: list of events for user_id
    """
    events = []
    for event in EventTable.scan(EventTable.user_id == user_id):
        events.append(event.attribute_values)
    return json.dumps(events)


def delete_all_events_by_user_id(user_id):
    """
    :param user_id:
    :return: status
    """
    events = EventTable.scan(EventTable.user_id == user_id)
    for event in events:
        event.delete()
    return json.dumps({"Method": f"DELETE", "user_id": f"{user_id}", "Status": "OK"})


def get_event_by_user_id_and_date(user_id, event_date):
    """
    :param user_id:
    :param event_date:
    :return: event
    """
    try:
        e = EventTable.get(user_id, event_date)
        return e.attribute_values
    except EventTable.DoesNotExist as e:
        return json.dumps({})


def delete_event_by_user_id_and_date(user_id, event_date):
    """
    :param user_id:
    :param event_date:
    :return: method, user_id, count, status
    """
    count = 0
    events = EventTable.scan((EventTable.user_id == user_id) & (EventTable.event_date == event_date))
    for event in events:
        event.delete()
        count += 1
    return json.dumps({"method": f"delete", "user_id": f"{user_id}", "count": f"{count}",
                       "date": f"{event_date}", "status": "ok"})


def list_locks_by_user_id(user_id):
    """
    :param user_id:
    :return: list of locks for user
    """
    locks = []
    for lock in LockTable.scan(LockTable.user_id == user_id):
        locks.append(lock.attribute_values)
    return json.dumps(locks)


def delete_all_locks_by_user_id(user_id):
    """
    :param user_id:
    :return: method, user_id, count, status
    """
    count = 0
    for lock in LockTable.scan(LockTable.user_id == user_id):
        lock.delete()
        count += 1
    return json.dumps({"method": f"delete", "user_id": f"{user_id}", "count": f"{count}", "status": "ok"})


def get_lock_by_user_id_and_date(user_id, event_date):
    """
    :param user_id:
    :param event_date:
    :return: lock for user
    """
    locks = LockTable.scan(LockTable.user_id == user_id, LockTable.event_date == event_date)
    for lock in locks:
        lock.delete()
    return json.dumps({"Method": f"DELETE", "user_id": f"{user_id}", "date": f"{event_date}", "Status": "OK"})


def delete_lock_by_user_id_and_date(user_id, event_date):
    """
    :param user_id:
    :param event_date:
    :return: status
    """
    locks = LockTable.scan((LockTable.user_id == user_id) & (LockTable.event_date == event_date))
    for lock in locks:
        lock.delete()
    return json.dumps({"Method": f"DELETE", "user_id": f"{user_id}", "date": f"{event_date}", "Status": "OK"})


def list_all_events():
    """
    :return: list of all events
    """
    events = []
    for event in EventTable.scan():
        events.append(event.attribute_values)
    return json.dumps(events)


def list_all_events_by_date(event_date):
    """
    :param event_date:
    :return: list of all events for date
    """
    events = []
    for event in EventTable.scan(EventTable.event_date == event_date):
        events.append(event.attribute_values)
    return json.dumps(events)


def create_event_v2(events):
    """
    :param events:
    :return: status
    """
    if isinstance(events, str):
        events = ast.literal_eval(events)
    event = EventTable(
        user_id=f"{events.get('user_id')}",
        event_date=f"{events.get('event_date')}",
        user_name=f"{events.get('user_name')}",
        reason=f"{events.get('reason')}",
        hours=f"{events.get('hours')}",
    )
    return json.dumps(event.save())


def delete_all_events_by_date(event_date):
    """
    :param event_date:
    :return: status
    """
    events = EventTable.scan(str(EventTable.event_date) == event_date)
    for event in events:
        event.delete()
    return json.dumps({"Method": f"DELETE", "date": f"{event_date}", "Status": "OK"})


def list_all_locks():
    """
    :return: list of all locks
    """
    locks = []
    for lock in LockTable.scan():
        locks.append(lock.attribute_values)
    return json.dumps(locks)


def create_lock(lock_request):
    """
    :param lock_request:
    :return: status
    """
    try:
        lock = LockTable(
            hash_key=f"{lock_request.get('user_id')}",
            range_key=f"{lock_request.get('event_date')}")
        return json.dumps(lock.save())
    except ClientError as e:
        log.debug(e.response['Error']['Message'])
        return json.dumps({"error": "Failed to create lock"})


def list_all_locks_by_date(event_date):
    """
    :param event_date:
    :return: list of locks for date
    """
    locks = []
    for lock in LockTable.scan(str(LockTable.event_date) == event_date):
        locks.append(lock.attribute_values)
    return json.dumps(locks)


def delete_all_locks_by_date(event_date):
    """
    :param event_date:
    :return: status
    """
    locks = LockTable.scan(str(LockTable.event_date) == event_date)
    for lock in locks:
        lock.delete()
    return json.dumps({"Method": f"DELETE", "date": f"{event_date}", "Status": "OK"})


##################################################
#                                                #
#      TODO: The following code is support for   #
#            v1 api                              #
#                                                #
##################################################


def get_id(user_id, start_date=None, end_date=None):
    """
    Get items for user. Optionally between start and end date.
    Status: Implemented
    """
    events = []
    if start_date and end_date:
        for event in EventTable.scan(
                (EventTable.event_date.between(start_date, end_date))
                & (EventTable.user_id == user_id)
        ):
            events.append(event.attribute_values)
    else:
        event = EventTable.scan(EventTable.user_id == user_id)
        for e in event:
            events.append(e.attribute_values)

    return json.dumps(events)


def create_event_v1(events, user_id=None):
    """
    :param events:
    :param user_id=None
    :return: status
    """
    if isinstance(events, str):
        events = ast.literal_eval(events)
    event = EventTable(
        user_id=user_id,
        event_date=f"{events.get('event_date')}",
        user_name=f"{events.get('user_name')}",
        reason=f"{events.get('reason')}",
        hours=f"{events.get('hours')}",
    )
    return json.dumps(event.save())


# Not implemented
def delete_event_v1(user_id, date):
    log.info(f'inside delete_event in dynamo backend: user_id is {user_id}, date is {date}')
    try:
        response = dynamoboto.table.delete_item(Key={'event_date': date, 'user_id': user_id})
    except ClientError as e:
        log.debug(e.response['Error']['Message'])
    else:
        log.debug(f"Delete item succeeded with response: {response}")
        return json.dumps(response, indent=4)
