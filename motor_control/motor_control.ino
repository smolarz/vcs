// #include <AccelStepper.h>
#include "AccelStepper.h"
#include "function.h"
#include "Axis.h"

// axis x_axis(3, 2, 4); // (pulse, direction and enabled pins)
axis x_axis(10, 9, 8);

axis y_axis(6, 5, 7); // (pulse, direction and enabled pins)
// axis z_axis(10, 9, 26); // (pulse, direction and enabled pins)
axis z_axis(4, 3, 2); // (pulse, direction and enabled pins)

static int stp = 0; // Step of the process (determines which function is called)
// static int stp = 2; // Step of the process (determines which function is called)

// Substrate dimensions [temporary, will be from serial communication]
// static double subW = 32.0; // mm, substrate width [Real one]
// static double subW = 3.0; // mm, substrate width [for tests]
static float subW = 3.0; // mm, substrate width [for tests]
// static double subL = 77.0; // mm, substrate length
static double subL = 2.0; // mm, substrate length
static double inc = 0.5; // mm, y distance between spray distance
static double dz = 2.5; // Distance between the nozzle and the substrate while spraying
static double dx; // Distance along x covered during spraying
static double dy; // Distance along y covered during spraying
static int n; // Number of necessary vertical increments
static int l = 1; // Number of layers
static int countn = 0; // Counting the y increments
static int countl = 0; // Counting layers
static float dt = 1000; // Time delay before starting to spray for flow stabilization

static double xspeed_mm = 0.5; // mm/s, speed of the x axis for the spray sequence
// static int xspeed; // step/s
static int xspeed = 500; // step/s

static double x = 0, y = 0, z = 0; // Actual ("live") position for each axis

// Absolute position where to start before spraying sequence (Default)
static double xstart = 164.3;
// static double xstart = 164.3 - 33.1; // For spraying in the center
static double ystart = 37.8;
// static double ystart = 37.8 - 13.375; // For spraying in the center 

// Manual mode displacement increments (or decrements)
static float dx_man = 1.0;
static float dy_man = 1.0;
static float dz_man = 1.0;

void setup() // ===========================================================================
{
  pinMode(A8, OUTPUT);
  analogWrite(A8, 0);
  // X AXIS
  x_axis.stepper->setAcceleration(5000);
  // set to max acceleration to eliminate this part
  // x_axis.stepper->disableOutputs();
  x_axis.disableOutput();
  x_axis.r =  x_axis.m * 200.0 / (5.0 * x_axis.gr); // Lead of ball screw : 5 mm

  // Y AXIS
  y_axis.stepper->setAcceleration(5000);
  // y_axis.stepper->disableOutputs();
  y_axis.disableOutput();
  y_axis.gr = 0.611 / 0.357;
  y_axis.r = y_axis.m * 200.0 / (0.1 * 25.4 * y_axis.gr); // Lead of ball screw : 0.1"

  // Z AXIS
  z_axis.stepper->setAcceleration(5000);
  // z_axis.stepper->disableOutputs();
  z_axis.disableOutput();
  z_axis.r =  z_axis.m * 200.0 / (0.1 * 25.4 * z_axis.gr); // Lead of ball screw : 0.1"

  /*
    // PUSHBUTTON
    pinMode(11, INPUT); // Pushbutton 1
    pinMode(12, INPUT); // Pushbutton 2
    pinMode(13, OUTPUT); // Test LED
    pinMode(26, OUTPUT);

    pinMode(A14, INPUT);
    pinMode(A15, INPUT);
  */

  /*
    // CONNECTIONS
    // All the pins for the limit switches of the three axis, the pin
    // for the zeroing of the nozzle, estimate of maximum distance to
    // nozzle up limit switch distance, etc.
    // [All analog pins in with a_to_d_in() function]
    x_axis.ls1 = 1;
    x_axis.ls2 = 2;
    y_axis.ls1 = 3;
    y_axis.ls2 = 4;
    z_axis.ls1 = 5;
    z_axis.ls2 = 6;
    z_axis.pinz = 7;

  */

  /*
    // Does not work for the analog pins in ***
    pinMode(x_axis.ls1, INPUT); // Home limit switch
    pinMode(x_axis.ls2, INPUT); // Far sire limit switch
    pinMode(y_axis.ls1, INPUT); // Home limit switch
    pinMode(y_axis.ls2, INPUT); // Far sire limit switch
    pinMode(z_axis.ls1, INPUT); // Home limit switch
    pinMode(z_axis.ls2, INPUT); // Far sire limit switch
    pinMode(z_axis.pinz, INPUT); // Closed circuit pin to zero nozzle w.r.t. substrate
  */
  x_axis.ls1 = 1;
  x_axis.ls2 = 2;
  y_axis.ls1 = 3;
  y_axis.ls2 = 4;
  z_axis.ls1 = 5;
  z_axis.ls2 = 6;
  z_axis.pinz = 7;


  pinMode(A1, INPUT); // LS1X
  pinMode(A2, INPUT); // LS2X
  pinMode(A3, INPUT); // LS1Y
  pinMode(A4, INPUT); // LS2Y
  pinMode(A5, INPUT); // LS1Z
  pinMode(A6, INPUT); // LS2Z
  pinMode(A7, INPUT); // PINZ
  pinMode(A8, INPUT); // For stop motion from the GUI

  // SERIAL COMMUNICATION
  Serial.begin(9600); // Set the baud rate, must be same than in Python
  while (!Serial)
  {
    // Waiting for the port to configure and start
  }
  // Serial.println("Communication established");
  Serial.flush();
}

void loop() // ============================================================================
{
  if (stop_check())  // Stopped from the GUI
  {
    stp = 1;
    // Serial.println(stp);
    Serial.println(101);
  }
  /*
    // if ((fabs(subW - 3.65) < 1e-2) && (fabs(subL - 77.5) < 1e-2) && (fabs(inc - 0.3) < 1e-2) && (fabs(l - 5) < 1e-2) && (fabs(xspeed - 0.55) < 1e-2) && (fabs(dz - 2.5) < 1e-2))
    if ((fabs(subW - 1.1) < 1e-2) && (fabs(subL - 1.1) < 1e-2) && (fabs(inc - 1.1) < 1e-2) && (fabs(xspeed_mm - 1.1) < 1e-2) && (fabs(dz - 1.1) < 1e-2) && (fabs(dt - 1100) < 1e-2))
    {
      digitalWrite(13, HIGH);
    } else {
      digitalWrite(13, LOW);
    }
  */

  if ((stp == 0) || (stp == 10) || (stp == 20) || (stp == 30) || (stp == 40) || (stp == 50) || (stp == 60) || (stp == 90))
  {
    while (Serial.available() == 0) {
      delay(1);
      // Verify stop pin **
      if (stop_check()) stp = 1;
    }
    if (Serial.available() > 0) {
      stp = Serial.parseInt();
      // if stp is bad, do something!

      // ******************************************************************
      // If one of the manual mode than wait for the appropriate delta value
      if ((stp == 15) || (stp == 16) || (stp == 25) || (stp == 26) || (stp == 35) || (stp == 36))
      {
        Serial.write('1');

        while (Serial.available() == 0)
        {
          delay(1);
          // Verify stop pin **
          if (stop_check()) stp = 1;
        }

        if (Serial.available() > 0)
        {
          // if((stp == 15) || (stp == 16))  { dx_man = Serial.parseFloat(); Serial.println(dx_man); }
          if ((stp == 15) || (stp == 16))  dx_man = Serial.parseFloat();
          else if ((stp == 25) || (stp == 26)) dy_man = Serial.parseFloat();
          else if ((stp == 35) || (stp == 36)) dz_man = Serial.parseFloat();
          else stp = 9; // [ERROR]
        }
      }
    }
  }

  // === x axis enable/disable ==================================================

  if ((stp > 0 && stp < 9) || (stp > 10 && stp < 18) || (stp > 40 && stp < 50) || (stp > 50 && stp < 60) || (stp > 60 && stp < 70))
  {
    // x_axis.stepper->enableOutputs();
    x_axis.enableOutput();
  } else {
    // x_axis.stepper->disableOutputs();
    x_axis.disableOutput();
  }


  // === y axis enable/disable ===
  if ((stp > 0 && stp < 9) || (stp > 20 && stp < 28) ||  (stp > 40 && stp < 50) || (stp > 50 && stp < 60) || (stp > 60 && stp < 70))
  {
    // y_axis.stepper->enableOutputs();
    y_axis.enableOutput();
  } else {
    // y_axis.stepper->disableOutputs();
    y_axis.disableOutput();
  }


  // === z axis enable/disable ===
  if ((stp > 0 && stp < 9) || (stp > 30 && stp < 39) || (stp > 40 && stp < 50) || (stp > 50 && stp < 60) || (stp > 60 && stp < 70))
  {
    // z_axis.stepper->enableOutputs();
    z_axis.enableOutput();
  } else {
    // z_axis.stepper->disableOutputs();
    z_axis.disableOutput();
    // z_axis.enableOutput();
  }

  /*
    // z_axis.disableOutput();
    static int flag = 0;
    static int count_flag = 0;
    // if (count_flag > 10000)
    if (count_flag > 1000)
    {
      count_flag = 0;
      if (flag > 0)
      {
        // z_axis.disableOutput();
        digitalWrite(26, HIGH);
        // Serial.println(digitalRead(8));
        Serial.println("Disabled");
        Serial.println(flag);
      }
      else if (flag == 0)
      {
        // z_axis.enableOutput();
        digitalWrite(26, HIGH);
        // Serial.println(digitalRead(8));
        Serial.println("Enabled");
        Serial.println(flag);
      }
    } else { count_flag++; }

    if (digitalRead(12))
    {
      if(flag == 0) flag = 1;
      else flag = 0;
      delay(300);
      Serial.println("PB");
    }
  */
  // === Set maxSpeed for manual mode ===

  // static double manx_mm = 0.8; // mm/s
  static double manx_mm = 8.0; // mm/s
  static int manx;
  manx = (manx_mm * x_axis.r); // steps/s

  static double many_mm = 0.8; // mm/s
  static int many;
  many = (many_mm * y_axis.r); // steps/s

  static double manz_mm = 0.8; // mm/s
  static int manz;
  manz = (manz_mm * z_axis.r); // steps/s


  /*
    static int manx = 500;
    static int many = 500;
    static int manz = 500;
  */
  
  static int autx = 8000;
  // static int autx = 0.75 * x_axis.r;
  static int auty = 8000;
  static int autz = 8000;

  static int zspeed = 1000; // For slower zeroing of the nozzle w.r.t. the substrate


  if ((stp == 15) || (stp == 16) || (stp == 25) || (stp == 26) || (stp == 35) || (stp == 36)) {
    x_axis.stepper->setMaxSpeed(manx);
    y_axis.stepper->setMaxSpeed(many);
    z_axis.stepper->setMaxSpeed(manz);
  } else if ((stp > 41) && (stp < 49))
  {
    xspeed = (xspeed_mm * x_axis.r); // steps/s
    x_axis.stepper->setMaxSpeed(xspeed);
    y_axis.stepper->setMaxSpeed(auty);
    z_axis.stepper->setMaxSpeed(autz);

  } else if (stp == 68)
  {
    x_axis.stepper->setMaxSpeed(autx);
    y_axis.stepper->setMaxSpeed(auty);
    z_axis.stepper->setMaxSpeed(zspeed);
  } else {
    x_axis.stepper->setMaxSpeed(autx);
    y_axis.stepper->setMaxSpeed(auty);
    z_axis.stepper->setMaxSpeed(autz);
  }

  // === LIVE POSITION ========================================================================

  x = x_axis.stepper->currentPosition() / x_axis.r;
  y = y_axis.stepper->currentPosition() / y_axis.r;
  z = z_axis.stepper->currentPosition() / z_axis.r;

  // === GUI COMM ===========================================================================

  // === Serial communication for step (for debugging purposes) ===
  /*
    static int stp_prev;
    if (stp_prev != stp)
    {
    Serial.println(stp);
    stp_prev = stp;
    }

    // === Receiving stp number [always] ===
    // [Corresponding Python script : test6.py]
    if (Serial.available())
    {
    // Receive the step info from the GUI

    }
  */

  // === STEPS ================================================================================

  if (stp == 0)
  {
    // Standby [Something else to reset?]
    x_axis.move_mm_reset();
    y_axis.move_mm_reset();
    z_axis.move_mm_reset();
  }

  if (stp == 1) // Emergency stop
  {
    // Pin to the emergency stop relay directly from the
    // RPi in case serial communication is not working well
    x_axis.move_mm_reset();
    y_axis.move_mm_reset();
    z_axis.move_mm_reset();
    stp = 10; //
    Serial.println(stp);
  }

  if (stp == 2) // Zero X and Y axes with limit switches
  {
    stp = 51;
  }

  if (stp == 3) // Zero nozzle
  {
    /*
      if (z_axis.zero_nozzle() == 3)
      {
      z_axis.move_mm_reset();
      stp = 4;
      }
    */
    // Substrate on top of the nozzle for rod zeroing
    if (!(x_axis.check_limit()) && !(y_axis.check_limit()))
    {
      if (y_axis.move_abs_mm(ystart - 15.0)) // For the center of the substrate to be more or less aligned with the nozzle center
      {
        if (x_axis.move_abs_mm(xstart - 38.0)) // For the center of the substrate to be more or less aligned with the nozzle center
        {
          stp = 63;
          // Serial.println(stp);
        }
      }
    } else {
      stp = 9;
      Serial.println(stp);
    }

  }

  if (stp == 4)
  {
    if (z_axis.move_mm(-10.0))
    {
      stp = 10;
      Serial.println(stp);
    }
  }


  if (stp == 5) // Go to home position
  {

    if (x_axis.go_home())
    {
      if (y_axis.go_home())
      {
        if (z_axis.go_home())
        {
          stp = 10;
          Serial.println(stp);
        }
      }
    }
  }

  if (stp == 6) // Remove substrate
  {
    if (z_axis.go_home())
    {
      if (y_axis.go_up())
      {
        if (x_axis.go_up() == 3)
        {
          stp = 10;
          Serial.println(stp);
        }
      }
    }
  }


  if (stp == 7) // Remove nozzle
  {
    if (!(x_axis.check_limit()) && !(y_axis.check_limit()) && !(z_axis.check_limit()))
    {
      if (x_axis.go_home())
      {
        if (y_axis.go_home())
        {
          if ((z_axis.go_up()) == 3)
          {
            stp = 10;
            Serial.println(stp);
          }
        }
      }
    }
  }

  if (stp == 8) // Go to origin of spray sequence
  {
    /*
      // NOW AT STEP 57 **
      // xstart, ystart
      xstart = x_axis.stepper->currentPosition() / x_axis.r;
      ystart = y_axis.stepper->currentPosition() / y_axis.r;
      stp = 0;
      Serial.println(stp);
    */

    if (!(x_axis.check_limit()) && !(y_axis.check_limit()))
    {
      if (y_axis.move_abs_mm(ystart))
      {
        if (x_axis.move_abs_mm(xstart))
        {
          stp = 10;
          Serial.println(stp);
        }
      }
    } else {
      stp = 9;
      Serial.println(stp);
    }
  }

  if (stp == 9)
  {
    // [ERROR] Limit switch encountered
    stp = 9;
    Serial.println(stp);
  }

  // === 10 === // X AXIS ===================================================================
  if (stp == 10)
  {
    // Standby
    x_axis.move_mm_reset();
  }

  if (stp == 11) // Relative motion
  {
    
      // Timing calcualtions
      static int init = 1;
      if (init)
      {
        Serial.println(millis());
        init = 0;
      }
    

    if (!x_axis.check_limit())
    {
      if (x_axis.move_mm(500.0))
      {
        Serial.println(millis());
        init = 1;
        stp = 10;
        Serial.println(stp);
      }
    } else {
      stp = 19;
      Serial.println(stp);
    }
  }

  if (stp == 12) // Absolute motion
  {
    if (x_axis.move_abs_mm(20.0))
    {
      stp = 10;
      Serial.println(stp);
    }
  }

  if (stp == 13) // Zero this axis
  {
    if (x_axis.zero() == 3)
    {
      stp = 14; // Go back home
    }
  }

  if (stp == 14) // Go home (this axis only)
  {
    if (!x_axis.check_home()) {
      if (x_axis.go_home())
      {
        x_axis.move_mm_reset();
        stp = 10;
        Serial.println(stp);
      }
    } else {
      stp = 19;
      Serial.println(stp);
    }
  }

  if (stp == 15) // Manual mode -- forward
  {
    /*
      // Previous way when the buttons / communication was continuous, at each loop
      if (!x_axis.check_far())
      {
      if (x_axis.move_abs_mm(x_axis.mx))
      {
        stp = 10;
        Serial.println(stp);
      }
      } else {
      stp = 19;
      Serial.println(stp);
      }
    */

    if (!x_axis.check_far())
    {
      if (x_axis.move_mm(dx_man))
      {
        stp = 10;
        Serial.println(stp);
      }
    } else {
      stp = 19;
      Serial.println(stp);
    }

  }

  if (stp == 16) // Manual mode -- backward
  {
    /*
      // Previous way when the buttons / communication was continuous, at each loop
      if (!x_axis.check_home())
      {
      if (x_axis.move_abs_mm(0.0))
      {
        stp = 10;
      }
      } else {
      stp = 19;
      Serial.println(stp);
      }
    */
    // Even if in the other direction send the information as positive
    if (!x_axis.check_home())
    {
      if (x_axis.move_mm(-1 * dx_man))
      {
        stp = 10;
        Serial.println(stp);
      }
    } else {
      stp = 19;
      Serial.println(stp);
    }

  }

  if (stp == 17) // Go to far side
  {
    if (!x_axis.check_limit())
    {
      if (x_axis.go_up() == 3)
      {
        stp = 10;
        Serial.println(stp);
      }
    } else {
      stp = 19;
      Serial.println(stp);
    }
  }

  if (stp == 19)
  {
    // [ERROR] Limit switch hit at wrong moment
    // To reset target to current position if changing direction
    x_axis.stepper->setCurrentPosition(x_axis.stepper->currentPosition());
    x_axis.move_mm_reset();
    stp = 10;
  }

  // === 20 === // Y AXIS ======================================================================
  if (stp == 20)
  {
    // Standby
    y_axis.move_mm_reset();
  }

  if (stp == 21) // Relative motion
  {
    /*
      // Timing calcualtions
      static int init = 1;
      if (init)
      {
        Serial.println(millis());
        init = 0;
      }
    */

    if (!y_axis.check_limit())
    {
      if (y_axis.move_mm(10.0))
      {
        // Serial.println(millis());
        // init = 1;
        stp = 20;
        Serial.println(stp);
      }
    } else {
      stp = 29;
      Serial.println(stp);
    }
  }

  if (stp == 22) // Absolute motion
  {
    if (y_axis.move_abs_mm(30.0))
    {
      stp = 20;
      Serial.println(stp);
    }
  }

  if (stp == 23) // Zero this axis
  {
    if (y_axis.zero() == 3)
    {
      stp = 24; // Go back home
    }
  }

  if (stp == 24) // Go home (this axis only)
  {
    if (!y_axis.check_home())
    {
      if (y_axis.go_home())
      {
        stp = 20;
        Serial.println(stp);
      }
    } else {
      stp = 29;
      Serial.println(stp);
    }
  }

  if (stp == 25) // Manual mode -- forward
  {
    if (!y_axis.check_far())
    {
      if (y_axis.move_mm(dy_man))
      {
        stp = 20;
        Serial.println(stp);
      }
    } else {
      stp = 29;
      Serial.println(stp);
    }
  }

  if (stp == 26) // Manual mode -- backward
  {
    if (!y_axis.check_home())
    {
      if (y_axis.move_mm(-1 * dy_man))
      {
        stp = 20;
        Serial.println(stp);
      }
    } else {
      stp = 29;
      Serial.println(stp);
    }
  }

  if (stp == 27) // Go to far side
  {
    if (!y_axis.check_limit())
    {
      if (y_axis.go_up() == 3)
      {
        stp = 20;
        Serial.println(stp);
      }
    } else {
      stp = 29;
      Serial.println(stp);
    }
  }

  if (stp == 29)
  {
    // Limit switch hit at wrong moment
    y_axis.stepper->setCurrentPosition(y_axis.stepper->currentPosition());
    y_axis.move_mm_reset();
    stp = 20;

  }

  // === 30 === // Z AXIS ======================================================================
  if (stp == 30)
  {
    // Standby
    z_axis.move_mm_reset();
  }

  if (stp == 31) // Relative motion
  {
    /*
      // Timing calcualtions
      static int init = 1;
      if (init)
      {
        Serial.println(millis());
        init = 0;
      }
    */

    if (!z_axis.check_limit())
    {
      if (z_axis.move_mm(10.0))
      {
        // Serial.println(millis());
        // init = 1;
        stp = 30;
        Serial.println(stp);
      }
    } else {
      stp = 39;
      Serial.println(stp);
    }
  }

  if (stp == 32) // Absolute motion
  {
    if (z_axis.move_abs_mm(20.0))
    {
      stp = 30;
      Serial.println(stp);
    }
  }

  if (stp == 33) // Zero this axis
  {
    if (z_axis.zero() == 3)
    {
      stp = 34; // Go back home
    }
  }

  if (stp == 34) // Go home (this axis only)
  {
    if (!z_axis.check_home())
    {
      if (z_axis.go_home())
      {
        stp = 30;
        Serial.println(stp);
      }
    } else {
      stp = 39;
      Serial.println(stp);
    }
  }

  if (stp == 35) // Manual mode -- forward
  {
    if (!z_axis.check_far())
    {
      if (z_axis.move_mm(dz_man))
      {
        stp = 30;
        Serial.println(stp);
      }
    } else {
      stp = 39;
      Serial.println(stp);
    }
  }

  if (stp == 36) // Manual mode -- backward
  {
    if (!z_axis.check_home())
    {
      if (z_axis.move_mm(-1 * dz_man))
      {
        stp = 30;
        Serial.println(stp);
      }
    } else {
      stp = 39;
      Serial.println(stp);
    }
  }

  if (stp == 37) // Go to far side
  {
    if (!z_axis.check_limit())
    {
      if (z_axis.go_up() == 3)
      {
        stp = 30;
        Serial.println(stp);
      }
    } else {
      stp = 39;
      Serial.println(stp);
    }
  }

  if (stp == 38) // Go to standoff distance
  {
    if (!z_axis.check_limit())
    {
      if (z_axis.move_abs_mm(z_axis.sub_height - dz))
      {
        stp = 30;
        Serial.println(stp);
      }
    } else {
      stp = 29;
      Serial.println(stp);
    }
  }

  if (stp == 39)
  {
    // Limit switch hit at wrong moment
    z_axis.stepper->setCurrentPosition(z_axis.stepper->currentPosition());
    z_axis.move_mm_reset();
    stp = 30;
  }

  // === 40 === // SPRAY SEQUENCE ==========================================================
  if (stp == 40)
  {
    // Standby
    x_axis.move_mm_reset();
    y_axis.move_mm_reset();
    z_axis.move_mm_reset();
  }

  /*
     For future work, if the substrate is a cylinder rather than a rectangle,
     the rotation of the cylinder would be executed by the y axis motor.
     [Or if both are desired, it would be very similar to the y axis]
  */

  if (stp == 41) // Starting position
  {
    if (!(x_axis.check_limit()) && !(y_axis.check_limit()))
    {
      if (y_axis.move_abs_mm(ystart))
      {
        if (x_axis.move_abs_mm(xstart))
        {
          stp = 42;
        }
      }
    } else {
      stp = 9;
      Serial.println(stp);
    }
  }

  if (stp == 42) // Position nozzle to appropriate height
  {
    if (z_axis.move_abs_mm(z_axis.sub_height - dz))
    {
      stp = 43;
    }
  }

  if (stp == 43)
  {
    // In the mean time calculate the distance to cover the substrate
    dx = subL + 5.0; // 2.5 mm on each side
    dy = subW + 4.0; // 2.0 mm on each side
    // Put each side's extra length as a variable at top to easily change [?]
    n = dy / inc;
    countn = 0;
    countl = 0;
    /*
        // Timing calcualtions
        static int init = 1;
        if (init)
        {
          // Serial.println(millis());
          init = 0;
        }
    */
    delay(dt); // Delay for the stabilization of the flow
    stp = 44;
  }

  if (stp == 44) // Spray forward (x axis)
  {
    if (!(x_axis.check_limit()))
    {
      if (x_axis.move_mm(-1 * dx))
      {
        stp = 45;
      }
    } else {
      stp = 9;
      Serial.println(stp);
    }
  }

  if (stp == 45) // Increment (y axis)
  {
    if (!(y_axis.check_limit()))
    {
      if (y_axis.move_mm(-1*inc))
      {
        countn++;
        stp = 46;
      }
    } else {
      stp = 9;
      Serial.println(stp);
    }
  }

  if (stp == 46) // Spray backward (x axis)
  {
    if (!(x_axis.check_limit()))
    {
      if (x_axis.move_mm(dx))
      {
        stp = 47;
      }
    } else {
      stp = 9;
      Serial.println(stp);
    }
  }

  if (stp == 47) // Increment (y axis)
  {
    if (!(y_axis.check_limit()))
    {
      if (y_axis.move_mm(-1*inc))
      {
        countn++;
        if (countn >= n)
        {
          countn = 0;
          stp = 49;
          // stp = 48; // If decrementing nozzle between layers (or number of layers)
        } else {
          stp = 44;
        }
      }
    } else {
      stp = 9;
      Serial.println(stp);
    }
  }

  if (stp == 48) // Decrement nozzle (z axis) [Currently not used]
  {
    if (!(z_axis.check_limit()))
    {
      if (z_axis.move_mm(-0.01))
      {
        stp = 48;
      }
    } else {
      stp = 9;
      Serial.println(stp);
    }
  }

  if (stp == 49) // Back to initial position for next layer
  {
    if (!(x_axis.check_limit()) && !(y_axis.check_limit()))
    {
      if (y_axis.move_abs_mm(ystart))
      {
        if (x_axis.move_abs_mm(xstart))
        {
          countl++;
          if (countl >= l)
          {
            countl = 0;
            // Serial.println(millis());
            stp = 40; // End of spray sequence
            Serial.println(stp);
          } else {
            stp = 44;
          }
        }
      }
    } else {
      stp = 9;
      Serial.println(stp);
    }
  }

  // === 50 === // ZERO SEQUENCE  ===================================================
  // Must do the zero separately
  if (stp == 50)
  {
    // Standby
    x_axis.move_mm_reset();
    y_axis.move_mm_reset();
    z_axis.move_mm_reset();
  }

  if (stp == 51) // Zero this axis
  {
    if (x_axis.zero() == 3)
    {
      // x_axis.move_mm_reset();
      stp = 52; // Go back home
    }
  }

  if (stp == 52) // Go home (this axis only)
  {
    if (x_axis.go_home())
    {
      x_axis.move_mm_reset();
      stp = 54;
    }
  }

  if (stp == 53) // Moves back 10 mm from the limit switch (not use anymore)
  {
    if (x_axis.move_mm(10.0))
    {
      stp = 54;
    }
  }

  if (stp == 54) // Zero this axis
  {
    if (y_axis.zero() == 3)
    {
      y_axis.move_mm_reset();
      stp = 55;
    }
  }

  if (stp == 55) // Go home (this axis only)
  {
    if (y_axis.go_home())
    {
      stp = 50;
      Serial.println(stp);
    }
  }

  if (stp == 56) // Moves back 10 mm from the limit switch (not use anymore)
  {
    if (y_axis.move_mm(10.0))
    {
      stp = 50;
    }
  }

  if (stp == 57) // Zero start position (origin for spray sequence)
  {
    // xstart, ystart
    xstart = x_axis.stepper->currentPosition() / x_axis.r;
    ystart = y_axis.stepper->currentPosition() / y_axis.r;
    stp = 50;
    Serial.println(stp);
  }

  if (stp == 58) // Zero nozzle [SLOWER], ** stp = 10 when over
  {
    /*
      if (z_axis.zero_nozzle_fine() == 3)
      {
      z_axis.move_mm_reset();
      stp = 4; // Goes back and then stp = 10 when over
      }
    */

    // Substrate on top of the nozzle for rod zeroing
    if (!(x_axis.check_limit()) && !(y_axis.check_limit()))
    {
      if (y_axis.move_abs_mm(ystart - 15.0))
      {
        if (x_axis.move_abs_mm(xstart - 38.0))
        {
          stp = 68;
          // Serial.println(stp);
        }
      }
    } else {
      stp = 9;
      Serial.println(stp);
    }
  }
  // === 60 // ZERO ROD ===================================================================
  if (stp == 60)
  {
    // Standby
    x_axis.move_mm_reset();
    y_axis.move_mm_reset();
    z_axis.move_mm_reset();
  }

  if (stp == 63) // Coarse zeroing with the rod
  {
    if (z_axis.zero_nozzle() == 3)
    {
      z_axis.move_mm_reset();
      stp = 4;
    }
  }

  if (stp == 68) // Fine zeroing with the rod
  {
    if (z_axis.zero_nozzle_fine() == 3)
    {
      z_axis.move_mm_reset();
      stp = 4; // Goes back and then stp = 10 when over
    }
  }

  // === 90 ===============================================================================

  if (stp == 90)
  {
    // Done/Standby
  }

  static int serialcomm = 0;
  static int dt_serialcomm = 0;
  if (stp == 91)
  {
    serialcomm = millis();
    // Serial.write('1'); // Worked with Windows (original one)
    Serial.println("1");

    while (Serial.available() == 0)
    {
      delay(1);
      // Verify stop pin **
      if (stop_check()) stp = 1;
    }

    if (Serial.available() > 0)
    {
      subW = Serial.parseFloat();
      stp = 92;
    }
  }

  if (stp == 92)
  {
    // Serial.write('2');
    Serial.println("2");

    while (Serial.available() == 0)
    {
      delay(1);
      // Verify stop pin **
      if (stop_check()) stp = 1;
    }

    if (Serial.available() > 0)
    {
      subL = Serial.parseFloat();
      stp = 93;
    }
  }

  if (stp == 93)
  {
    // Serial.write('3');
    Serial.println("3");

    while (Serial.available() == 0)
    {
      delay(1);
      // Verify stop pin **
      if (stop_check()) stp = 1;
    }

    if (Serial.available() > 0)
    {
      inc = Serial.parseFloat();
      stp = 94;
    }
  }

  if (stp == 94)
  {
    // Serial.write('4');
    Serial.println("4");

    while (Serial.available() == 0)
    {
      delay(1);
      // Verify stop pin **
      if (stop_check()) stp = 1;
    }

    if (Serial.available() > 0)
    {
      l = (int) Serial.parseFloat();
      stp = 95;
    }
  }

  if (stp == 95)
  {
    // Serial.write('5');
    Serial.println("5");

    while (Serial.available() == 0)
    {
      delay(1);
      // Verify stop pin **
      if (stop_check()) stp = 1;
    }

    if (Serial.available() > 0)
    {
      xspeed_mm = Serial.parseFloat();
      stp = 96;
    }
  }

  if (stp == 96)
  {
    // Serial.write('6');
    Serial.println("6");

    while (Serial.available() == 0)
    {
      delay(1);
      // Verify stop pin **
      if (stop_check()) stp = 1;
    }

    if (Serial.available() > 0)
    {
      dz = Serial.parseFloat();
      stp = 97;
    }
  }

  if (stp == 97)
  {
    // Serial.write('7');
    Serial.println("7");

    while (Serial.available() == 0)
    {
      delay(1);
      // Verify stop pin **
      if (stop_check()) stp = 1;
    }

    if (Serial.available() > 0)
    {
      dt = Serial.parseFloat();
      dt = dt * 1000;
      stp = 98;
    }

    // dt_serialcomm = millis() - serialcomm;
    // Serial.println(dt_serialcomm);
  }

  if (stp == 98)
  {
    Serial.println("8");
    stp = 90;
  }

  if (stp == 200)
  {
    Serial.println(subW);
    Serial.println(subL);
    Serial.println(inc);
    Serial.println(l);
    Serial.println(xspeed_mm);
    Serial.println(dz);
    Serial.println(dt);
    stp = 0;
  }

} // End of loop()

