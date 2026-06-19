#include "Geiger.h"

#include <Arduino.h>

Geiger::Geiger(byte pin, unsigned short size) : _queue(size)
{
  _pin = pin;
}

bool Geiger::enqueueItem(unsigned long item)
{
  if (!_queue.isFull())
  {
    _queue.enqueue(item);
    return true;
  }
  else
  {
    return false;
  }
}

unsigned long Geiger::dequeueItem()
{
  if (!_queue.isEmpty())
  {
    return _queue.dequeue();
  }
  else
  {
    return 0;
  }
}

unsigned short Geiger::getQueueCount()
{
  return _queue.itemCount();
}
