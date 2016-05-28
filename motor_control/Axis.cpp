// #include <AccelStepper.h>
#include "AccelStepper.h"
#include "function.h"
#include "Axis.h"

// =====================================
//          CONSTRUCTOR
// =====================================

axis::axis(int p, int d, int e) {

  stepper = new AccelStepper(1, p, d); // First argument is for the type, that is 4 wires
  // pulse and direct with respective comparison signals

  // stepper->setEnablePin(e);
  ena_pin = e;

  m = 8; // Microstep values

  // Number of steps per revolution = m*200
  // Lead = 0.05" * (25.4 mm / 1")
  // r = m * 200.0 / (0.1 * 25.4);
  // [Now outside script]

/*
  // [TO REMOVE]
  ls1 = 14;
  ls2 = 15;
  pinz = 15; // Temporary pin for zeroing axis (closed circuit)
  */

  // Default "safe" values
  sub_height = 50.0; 
  mx = 50.0;
  nozzle_offset = 10.0;

  init_rel = 1;

  return;
}

int axis::enableOutput(){
  digitalWrite(ena_pin, HIGH);
  return 0;
}

int axis::disableOutput(){
  digitalWrite(ena_pin, LOW);
  return 0;
}

// =====================================
//          MEMBER FUNCTIONS
// =====================================
// RELATIVE MOTION
int axis::move_mm(double mm) {
  // return = 0 : In progress
  // return = 1 : Done

  // Unsigned long instead of int to allow to hold larger numbers
  static unsigned long obj;
  static unsigned long init_pos;
  static unsigned long pos;

  if (init_rel)
  {
    obj = r * mm;
    stepper->move(obj);
    init_pos = stepper->currentPosition();
    init_rel = 0;
  }

  pos = stepper->currentPosition() - init_pos;

  if (pos != obj)
  {
    stepper->run();
    // stepper->runSpeedToPosition();
    
    // if (digitalRead(13) == 1) estop = 1;
    // if (estop_check(estop)) flag = 0;
    return 0;
  } else {
    stepper->stop();
    // stepper->runToPosition();
    init_rel = 1;
    return 1;
  }
}

int axis::move_mm_reset() {

  init_rel = 1;

  return 0;
}

// ABSOLUTE MOTION
int axis::move_abs_mm(double mm) {
  static unsigned long obj;
  obj = r * mm;
  // if (obj > mx) {obj = mx;} // Does not work !?
  stepper->moveTo(obj);

  if (stepper->currentPosition() != obj)
  {
    stepper->run();
    return 0;
  } else {
    stepper->stop();
    stepper->runToPosition();
    return 1;
  }
}

// ZEROING AXES
int axis::zero() {
  static int sub_stp = 0;
  static int init = 1;
  if (sub_stp == 0)
  {
    static double d_step = -60.0;
    if (move_mm(d_step))
    {
      d_step -= 60.0;
    }

    if (a_to_d_in(ls1))
    {
      stepper->setCurrentPosition(0);
      stepper->stop();
      move_mm_reset();
      sub_stp = 1;
    } else return 0;
  } else if (sub_stp == 1) {

    // if (init)
    if(0)
    {
      move_mm_reset();
      init = 0;
    }

    if (move_mm(5.0))
    {
      stepper->setCurrentPosition(0);
      stepper->stop();
      init = 1;
      move_mm_reset();
      sub_stp = 2;
    }
  } else if (sub_stp == 2) {
    static double d_step2 = 60.0;
    // if (init)
    if(0)
    {
      move_mm_reset();
      init = 0;
    }

    if (move_mm(d_step2))
    {
      d_step2 += 60.0;
    }

    if (a_to_d_in(ls2))
    {
      mx = stepper->currentPosition() / r - 3.75;
      sub_stp = 0;
      stepper->stop();
      stepper->setCurrentPosition(stepper->currentPosition()); // Resets target position to where it is
      // init = 1;
      move_mm_reset();
      return 3; // Must return value different from 1 because the move functions already
      // return 1 to everything and thus finishes all steps instead of only the sub step
    } else return 0;
  }
}

// ZEROING NOZZLE WITH CLOSE CIRCUIT
int axis::zero_nozzle() {
  // Same as the zero() function but has the pinz instead of the second limit switch
  static int sub_stp = 0;
  static int init = 1;
  if (sub_stp == 0)
  {
    static double d_step = -60.0;
    if (move_mm(d_step))
    {
      d_step -= 60.0;
    }

    if (a_to_d_in(ls1))
    {
      stepper->setCurrentPosition(0);
      stepper->stop();
      move_mm_reset();
      sub_stp = 1;
    } else return 0;
  } else if (sub_stp == 1) {
    if (init)
    {
      move_mm_reset();
      init = 0;
    }

    if (move_mm(5.0))
    {
      stepper->setCurrentPosition(0);
      stepper->stop();
      init = 1;
      move_mm_reset();
      sub_stp = 2;
    }
  } else if (sub_stp == 2) {
    static double d_step2 = 60.0;
    if (init)
    {
      move_mm_reset();
      init = 0;
    }

    if (move_mm(d_step2))
    {
      d_step2 += 60.0;
    }

    if (a_to_d_in(pinz))
    {
      sub_height = stepper->currentPosition() / r + nozzle_offset; 
      sub_stp = 0;
      stepper->stop();
      stepper->setCurrentPosition(stepper->currentPosition()); // Resets target position to where it is
      init = 1;
      return 3; // Must return value different from 1 because the move functions already
      // return 1 to everything and thus finishes all steps instead of only the sub step
    } else return 0;
  }
}

int axis::zero_nozzle_fine() {
  static int init = 1;
  static double d_step = 60.0;
  if (init)
  {
    move_mm_reset();
    init = 0;
  }

  if (move_mm(d_step))
  {
    d_step += 60.0;
  }

  if (a_to_d_in(pinz))
  {
    sub_height = stepper->currentPosition() / r + nozzle_offset; 
    stepper->stop();
    init = 1;
    return 3; // Must return value different from 1 because the move functions already
    // return 1 to everything and thus finishes all steps instead of only the sub step
  } else return 0;
}

// GO TO HOME POSITION
int axis::go_home() {
  static int obj = 0;
  stepper->moveTo(obj);
  if ((stepper->currentPosition()) == obj)
  {
    return 1;
  } else {
    stepper->run();
  }

  return 0;
}

// GO OPPOSITE TO HOME POSITION
int axis::go_up() {

  if (move_abs_mm(mx))
  {
    return 3;
  } else {
    return 0;
  }
}

int axis::go_up_nozzle(double standoff) {
  static double obj = sub_height - standoff;
  if (move_abs_mm(20.0))
  {
    return 3;
  } else {
    return 0;
  }
}

// Verification functions
int axis::check_limit() {
  // Check if any limit switch is encountered
  if (check_home() || check_far())
  {
    return 1;
  } else {
    return 0;
  }
}

int axis::check_home() {
  // if (digitalRead(ls1))
  if (a_to_d_in(ls1))
  {
    return 1;
  } else {
    return 0;
  }
}

int axis::check_far() {
  // if (digitalRead(ls2))
  if (a_to_d_in(ls2))
  {
    return 1;
  } else {
    return 0;
  }
}

// =====================================
//          DESTRUCTOR
// =====================================
axis::~axis() {

  if (stepper != NULL)
  {
    delete stepper;
    stepper = NULL;
  } else
  {
    // Debugging file?
  }

  return;
}

