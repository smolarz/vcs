class axis {

  public :
    // Member variables ====================================================================
    AccelStepper * stepper;
    int ena_pin;
    int ls1; // First limit switch pin (home)
    int ls2; // Second limit switch pin (far side)
    int pinz; // Pin for close circuit to zero nozzle with respect to substrate
    int estop;
    int m; // microsteps from the driver (to convert to distances)
    double r; // ratio to between steps to mm [steps/mm]
    int limit; // How many steps between limit switches
    double mx; // Maximum distance in mm between the two limit switches
    double nozzle_offset; // Offset for the nozzle zeroing
    double sub_height; // Distance in mm from home limit switch from substrate (analoguous to mx for other axes)
    int init_rel; // Flag use to initialize the objective of the relative motion function
    double gr = 1.0; // Gear ratio for the belt of the y axis (1.0 for the other axes)
    

    // Member functions =====================================================================
    axis(int p, int d, int e); // Constructor(pulse, direction and enabled pins)
    int enableOutput(); // Enable the motor through the ENA pin
    int disableOutput(); // Disable the motor through the ENA pin

    int move_mm(double mm); // Moves mm from current position (relative)
    int move_mm_reset(); // Reset objective of relative motion
    int move_abs_mm(double mm); // Moves to position in mm (absolute)
    int zero(); // Resets zero by reaching limit switch
    int zero_nozzle(); // Zero nozzle vertically with respect to substrate
    int zero_nozzle_fine(); // Second finer/slower pass to zero nozzle
    int go_home(); // Goes to home position
    int go_up(); // Opposite end of home position
    int go_up_nozzle(double standoff); // Go to substrate (with proper standoff distance)

    // Verification functions
    int check_limit(); // Check if limit switch encountered
    int check_home(); // Check if home limit switch is hit
    int check_far(); // Check if far limit switch is hit
    

    ~axis(); // Destructor

};

