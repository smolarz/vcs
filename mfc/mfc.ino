/* --------------------------------------------------------- */
/* ----------------- Mass flow controller ------------------ */
/* Author: Stacey Smolash ---------------------------------- */
/* Date:   February 2016  ---------------------------------- */
/* --------------------------------------------------------- */
/* NOTES: ************************************************** */
/* Output DAC0 to V- op-amp ******************************** */
/* Output DAC1 to V+ op-amp ******************************** */
/* DAC0 should always output 0 (dec) to remove 0.55 V offset */
/* Output of op-amp is input to MFC setpoint *************** */
/* --------------------------------------------------------- */

/* set constants */
const int timeout = 1000;            // timeout time (ms)
const float gain = 1.36;             // op-amp gain
const float DAC0_V = 0.55;           // DAC0 output (V)

const int minDAC_dec = 0;            // min DAC output (dec)
const int maxDAC_dec = 4095;         // max DAC output (dec)
const float minDAC_V = 0.55;         // min DAC output (V)
const float maxDAC_V = 2.75;         // max DAC output (V)

const int minADC_dec = 0;            // min ADC input (dec)
const int maxADC_dec = 4095;         // max ADC input (dec)
const float minADC_V = 0.0;          // min ADC input (V)
const float maxADC_V = 3.3;          // max ADC input (V)

const float minSetpoint_slpm = 0.0;  // min setpoint (slpm)
const float maxSetpoint_slpm = 15.0; // max setpoint (slpm)
const float minSetpoint_V = 0.0;     // min setpoint (V)
const float maxSetpoint_V = 3.0;     // max setpoint (V)

/* initialize global variables */
float serialIn = 0.0;                // incoming serial data from GUI (slpm)
float serialOut = 0.0;               // outgoing serial data to GUI (slpm)
float DAC1_V = 0.0;                  // DAC1 output (V)
int DAC1_dec = 0;                    // DAC1 output (dec)
float setpoint_V = 0.0;              // MFC setpoint (V)
int feedback_dec = 0;                // MFC feedback (dec)
float feedback_V = 0.0;              // MFC feedback (V)

void setup() {

  /* set up serial communication */
  Serial.begin(9600);                // open serial port, set data rate to 9600 bps
  Serial.flush();
  //Serial.setTimeout(timeout);        // set time to wait for incoming serial data

  /* configure pin modes (not required for DACs) */
  pinMode(A11, OUTPUT);                // use analog pin A11 for PWM out for valve override
  pinMode(A9, INPUT);                  // use analog pin A9 for feedback

  /* set analog resolution to 12 bits */
  analogWriteResolution(12);         // exploit full 12-bit DAC resolution (ie. can use analogWrite() with values between 0 and 4095)
  analogReadResolution(12);          // exploit full 12-bit ADC resolution (ie. can use analogRead() with values between 0 and 4095)
  
}

void loop() {

  // wait for serial data
  while (Serial.available() == 0) {
    delay(1);    
  }

  // if serial data is available 
  if (Serial.available() > 0) {

    // read in serial data (flowrate in slpm)
    serialIn = Serial.parseFloat();
    //Serial.println(serialIn); // test
    
    // if desired setpoint is within acceptable range
    if (serialIn >= minSetpoint_slpm && serialIn <= maxSetpoint_slpm) {
      
      // convert setpoint from slpm to V
      setpoint_V = map(serialIn*10, minSetpoint_slpm*10, maxSetpoint_slpm*10, minSetpoint_V*100, maxSetpoint_V*100);
      setpoint_V = setpoint_V/100;
      //Serial.println(setpoint_V); // test

      // compute DAC1 voltage required for specified setpoint (differential amplifier)
      DAC1_V = setpoint_V/gain + DAC0_V;
      //Serial.println(DAC1_V); // test

      // convert DAC1 from V to dec
      DAC1_dec = map(DAC1_V*100, minDAC_V*100, maxDAC_V*100, minDAC_dec, maxDAC_dec);
      //Serial.println(DAC1_dec); // test

      // write data to DAC0 pin
      analogWrite(DAC0, minDAC_dec);

      // write data to DAC1 pin
      analogWrite(DAC1, DAC1_dec);

      // pause program for 1 second
      //delay(1000);
      Serial.println("300");
      //Serial.flush();

      // read in feedback data and send feedback to GUI until GUI stop button is pushed
      while(1) {
        Serial.flush();
        // wait for serial data
        while (Serial.available() == 0) {
          delay(1);
        }

        if (Serial.available() > 0) {
          
          // read in serial data
          serialIn = Serial.parseInt();
          //Serial.println(serialIn); // test

          // wait for GUI prompt
          if (serialIn == 200) {
        
            // read feedback to A9 pin
            feedback_dec = analogRead(A9);
            //Serial.println(feedback_dec); // test

            // convert feedback from dec to V
            feedback_V = map(feedback_dec, minADC_dec, maxADC_dec, minADC_V*100, maxADC_V*100);
            feedback_V = feedback_V/100;
            //Serial.println(feedback_V); // test

            // convert feedback from V to slpm
            serialOut = map(feedback_V*100, minSetpoint_V*100, maxSetpoint_V*100, minSetpoint_slpm*100, maxSetpoint_slpm*100);
            serialOut = serialOut/100;

            // output serial data
            Serial.println(String(serialOut));
            //Serial.println('8');

           }

           // check if GUI stop button was pressed
           else if (serialIn == 100) {
            
            // write 0 (dec) to PWM pin A11 for valve close override
            analogWrite(A11, 0);

            // pause program for 1 second
            delay(1500);

            // read feedback to A9 pin
            feedback_dec = analogRead(A9);
            //Serial.println(feedback_dec); // test
            
            // convert feedback from dec to V
            feedback_V = map(feedback_dec, minADC_dec, maxADC_dec, minADC_V*100, maxADC_V*100);
            feedback_V = feedback_V/100;
            //Serial.println(feedback_V); // test

            // convert feedback from V to slpm
            serialOut = map(feedback_V*100, minSetpoint_V*100, maxSetpoint_V*100, minSetpoint_slpm*100, maxSetpoint_slpm*100);
            serialOut = serialOut/100;

            // output serial data
            Serial.println(String(serialOut));
            //Serial.println('0');

            // return from loop()
            Serial.flush();
            return;
            
           }

           else {
            Serial.flush();
           }
        }
      }
    }
  }
}

