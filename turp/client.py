# -*- coding: utf-8 -*-
import uuid
import time
from redis import Redis
import simplejson as json

class Client:
  def __init__(self):
    self.r = Redis()

  def random_key(self):
    return str(uuid.uuid4())

  def send_request(self, queue_name, method, *params):
    id = self.random_key()

    # Remove blank arrays
    if not params:
      params = None

    begin_time = time.time()*1000000

    request = {'jsonrpc': '2.0',
               'id': id,
               'queue_start_time': begin_time,
               'method': method,
               'params': params}
    self.r.lpush(queue_name, json.dumps(request))
    self.r.expire(queue_name, 10)
    print "Sent request {} to queue {}".format(id, queue_name)
    return id

  def get_response(self, id):
    channel, response = self.r.brpop(id)
    response_data = json.loads(response)

    id     = response_data['id']
    queue_start_time = response_data['queue_start_time']
    queue_end_time   = response_data['queue_end_time']
    work_end_time    = response_data['work_end_time']
    queue_time = int(queue_end_time - queue_start_time)
    work_time  = int(work_end_time - queue_end_time)

    print 'id: {}'.format(id)
    print '  queue_time: {} us'.format(queue_time)
    print '  work_time : {} us'.format(work_time)

    if 'result' in response_data:
        print 'Got response {}'.format(response_data)
    elif 'error' in response_data:
        print 'Got response {}'.format(response_data)

    return response_data
