#include "Arduino.h"

int a_to_d_in(int pin)
{
  int readIn;
  double vIn;
  readIn = analogRead(pin);
  vIn = (map(readIn, 0, 1023, 0*100, 5*100))/100;

  if (vIn > 2.5) return 1;
  else return 0;
}

int stop_check()
{
  a_to_d_in(8);
}
