#pragma once
#ifndef GEIGER_H
#define GEIGER_H

#include <Arduino.h>
#include <ArduinoQueue.h>

#define QUEUE_SIZE 100;

class Geiger
{
  public:
    Geiger(byte pin, unsigned short size);

    bool enqueueItem(unsigned long);
    unsigned long dequeueItem();
    unsigned short getQueueCount();

  private:
    int _pin;
    ArduinoQueue<unsigned long> _queue;
};

#endif
