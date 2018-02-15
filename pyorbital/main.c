/*
 * KubOS RT
 * Copyright (C) 2016 Kubos Corporation
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
/**************************************************************************
Pocketqubeshop
Module name                     : main.c
Date of last modification       : 08/09/2016
last update                     : created
Author                          : Anna Lito Michala
 **************************************************************************/

#include <errno.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <msp430.h>

#include "driverlib.h"

#define EPS_INTERNAL_I2C
#define EPS_EXTERNAL_I2C_SLAVE

#ifndef ULONG_MAX
#define ULONG_MAX       0xffffffff      //This is a FreeRTOS value that was not
#endif                                  //recognised by the compiler so it is re-defined

int i = 0;
char uartRxQueue[4];
int uartRxCounter = 0;

unsigned char i2cTXData;
//unsigned char i2cRXData;
volatile unsigned char RXData[10];
volatile unsigned int RXDataIndex;

unsigned char i2cB0RXByteCtr;
volatile unsigned char i2cB0RXBuffer[128];
unsigned char *pi2cB0RXData;

unsigned char i2cB0TXByteCtr;
volatile unsigned char i2cB0TXBuffer[128];
unsigned char *pi2cB0TXData;

unsigned char i2cB1RXByteCtr;
volatile unsigned char i2cB1RXBuffer[128];
unsigned char *pi2cB1RXData;

unsigned char i2cB1TXByteCtr;
volatile unsigned char i2cB1TXBuffer[128];
unsigned char *pi2cB1TXData;

unsigned char receivedData[4];


void perform_internal_i2c_write(void)
{
    if (i2cB1TXByteCtr == 0) return;

    pi2cB1TXData = (unsigned char *) i2cB1TXBuffer;

    if (i2cB1RXByteCtr == 1)
    {
        while (UCB1CTL1 & UCTXSTP);
        UCB1CTL1 |= UCTR + UCTXSTT;
        __bis_SR_register(LPM0_bits + GIE);
        __no_operation();
    }
    else
    {
        UCB1CTL1 |= UCTR + UCTXSTT;
        __bis_SR_register(LPM0_bits + GIE);
        __no_operation();
        while (UCB1CTL1 & UCTXSTP);
    }

}


void perform_internal_i2c_read(void)
{
    if (i2cB1RXByteCtr == 0) return;

    pi2cB1RXData = (unsigned char *)i2cB1RXBuffer;

    UCB1CTL1 &= ~UCTR;  //clear the i2c TX bit

    if (i2cB1RXByteCtr == 1)
    {
        while (UCB1CTL1 & UCTXSTP);             // Ensure stop condition got sent
        UCB1CTL1 |= UCTXSTT;                    // I2C start condition
        while(UCB1CTL1 & UCTXSTT);              // Start condition sent?
        UCB1CTL1 |= UCTXSTP;                    // I2C stop condition
    }
    else
    {
        while (UCB1CTL1 & UCTXSTP);
        UCB1CTL1 |= UCTXSTT;
    }

    __bis_SR_register(LPM0_bits + GIE);
    __no_operation();
}


void perform_external_i2c_write(void)
{
    if (i2cB0TXByteCtr == 0) return;

    pi2cB0TXData = (unsigned char *) i2cB0TXBuffer;

    if (i2cB0TXByteCtr == 1)
    {
        while (UCB0CTL1 & UCTXSTP);
        UCB0CTL1 |= UCTR + UCTXSTT;
        __bis_SR_register(LPM0_bits + GIE);
        __no_operation();
    }
    else
    {
        UCB0CTL1 |= UCTR + UCTXSTT;
        __bis_SR_register(LPM0_bits + GIE);
        __no_operation();
        while (UCB0CTL1 & UCTXSTP);
    }

}


void perform_external_i2c_read(void)
{
        if (i2cB0RXByteCtr == 0) return;

        pi2cB0RXData = (unsigned char *)i2cB0RXBuffer;

        UCB0CTL1 &= ~UCTR;  //clear the i2c TX bit

        if (i2cB0RXByteCtr == 1)
        {
            while (UCB0CTL1 & UCTXSTP);             // Ensure stop condition got sent
            UCB0CTL1 |= UCTXSTT;                    // I2C start condition
            while(UCB0CTL1 & UCTXSTT);              // Start condition sent?
            UCB0CTL1 |= UCTXSTP;                    // I2C stop condition
        }
        else
        {
            while (UCB0CTL1 & UCTXSTP);
            UCB0CTL1 |= UCTXSTT;
        }

        __bis_SR_register(LPM0_bits + GIE);
        __no_operation();
}



#ifdef EPS_INTERNAL_I2C

// i2c interrupt handler for rx and tx
#pragma vector = USCI_B1_VECTOR
__interrupt void USCI_B1_ISR(void)
{
    switch(__even_in_range(UCB1IV,12))
    {
    case  0: break;                           // Vector  0: No interrupts
    case  2: break;                           // Vector  2: ALIFG
    case  4: break;                           // Vector  4: NACKIFG
    case  6:                                  // Vector  6: STTIFG
       UCB1IFG &= ~UCSTTIFG;                  // Clear start condition int flag
       break;
    case  8:                                  // Vector  8: STPIFG
      i2cTXData++;                               // Increment TXData
      UCB1IFG &= ~UCSTPIFG;                   // Clear stop condition int flag
      break;
    case 10:                            // Vector 10: RXIFG
        if (i2cB1RXByteCtr == 1)
        {
                //i2cRXData = UCB1RXBUF;            // Get RX data
            *pi2cB1RXData = UCB1RXBUF;
            __bic_SR_register_on_exit(LPM0_bits);
        }
        else
        {
          i2cB1RXByteCtr--;
          if (i2cB1RXByteCtr)
          {
              *pi2cB1RXData++ = UCB1RXBUF;
              if (i2cB1RXByteCtr == 1)
              {
                  UCB1CTL1 |= UCTXSTP;
              }
          }
          else
          {
              *pi2cB1RXData = UCB1RXBUF;                     // Get RX data
              __bic_SR_register_on_exit(LPM0_bits);
          }
        }
      break;
    case 12:                                  // Vector 12: TXIFG
        if (i2cB1TXByteCtr)                          // Check TX byte counter
            {
              UCB1TXBUF = *pi2cB1TXData++;                   // Load TX buffer
              i2cB1TXByteCtr--;                          // Decrement TX byte counter
            }
            else
            {
              UCB1CTL1 |= UCTXSTP;                  // I2C stop condition
              UCB1IFG &= ~UCTXIFG;                  // Clear USCI_B1 TX int flag
              __bic_SR_register_on_exit(LPM0_bits); // Exit LPM0
            }

        break;
    default: break;
    }

}

#endif

#ifdef EPS_EXTERNAL_I2C

// i2c interrupt handler for rx and tx
#pragma vector = USCI_B0_VECTOR
__interrupt void USCI_B0_ISR(void)
{
    switch(__even_in_range(UCB0IV,12))
    {
    case  0: break;                           // Vector  0: No interrupts
    case  2: break;                           // Vector  2: ALIFG
    case  4: break;                           // Vector  4: NACKIFG
    case  6:                                  // Vector  6: STTIFG
       UCB0IFG &= ~UCSTTIFG;                  // Clear start condition int flag
       break;
    case  8:                                  // Vector  8: STPIFG
      i2cTXData++;                               // Increment TXData
      UCB0IFG &= ~UCSTPIFG;                   // Clear stop condition int flag
      break;
    case 10:                            // Vector 10: RXIFG
        if (i2cB0RXByteCtr == 1)
        {
                //i2cRXData = UCB0RXBUF;            // Get RX data
            *pi2cB0RXData = UCB0RXBUF;
            __bic_SR_register_on_exit(LPM0_bits);
        }
        else
        {
          i2cB0RXByteCtr--;
          if (i2cB0RXByteCtr)
          {
              *pi2cB0RXData++ = UCB0RXBUF;
              if (i2cB0RXByteCtr == 1)
              {
                  UCB0CTL1 |= UCTXSTP;
              }
          }
          else
          {
              *pi2cB0RXData = UCB0RXBUF;                     // Get RX data
              __bic_SR_register_on_exit(LPM0_bits);
          }
        }
      break;
    case 12:                                  // Vector 12: TXIFG
        if (i2cB0TXByteCtr)                          // Check TX byte counter
            {
              UCB0TXBUF = *pi2cB0TXData++;                   // Load TX buffer
              i2cB0TXByteCtr--;                          // Decrement TX byte counter
            }
            else
            {
              UCB0CTL1 |= UCTXSTP;                  // I2C stop condition
              UCB0IFG &= ~UCTXIFG;                  // Clear USCI_B0 TX int flag
              __bic_SR_register_on_exit(LPM0_bits); // Exit LPM0
            }


        break;
    default: break;
    }

}

#endif


#ifdef EPS_EXTERNAL_I2C_SLAVE

// USCI_B0 Data ISR
#pragma vector = USCI_B0_VECTOR
__interrupt void USCI_B0_ISR(void)
{
    switch(__even_in_range(UCB0IV,12))
    {
    case  0: break;                           // Vector  0: No interrupts
    case  2: break;                           // Vector  2: ALIFG
    case  4: break;                           // Vector  4: NACKIFG
    case  6: break;                           // Vector  6: STTIFG
    case  8: break;                           // Vector  8: STPIFG
    case 10:                                  // Vector 10: RXIFG
    if (RXDataIndex == 9)
    {
        RXDataIndex = 0;
    }
    RXData[RXDataIndex] = UCB0RXBUF;                     // Get RX data
    RXDataIndex++;
    break;

    case 12: break;                           // Vector 12: TXIFG
    default: break;
    }
}

#endif


int main(void)
{
    int i;
    uint8_t data;
    WDTCTL = WDTPW + WDTHOLD;                 // Stop WDT


    ////////////////
    //Setup Pin 2.4 to control ResetOBC signal - HI-LO-HI (or LO-HI-LO - looks for edge - which edge? - would be good to find out).
    ////////////////

    P2DIR |= 0x10;
    P2OUT &= ~0x10;
    P2OUT |= 0x10;
    P2OUT &= ~0x10;
    //    P2OUT |= 0x10;


    /////////////
    //// for test: setup pin 2.3 resetBRO
    //////////////////
    //    P2DIR |= 0x08;
    //    P2OUT |= 0x08;




    //    P2DIR |= 0x10;
    P2OUT &= ~0x10;
    //    while (1)
    //    {
    //        P2OUT ^= 0x10;
    //        P2OUT ^= 0x08;
    //    }
    P2OUT |= 0x10;
    P2OUT &= ~0x10;
    P2OUT |= 0x10;


    //    P6DIR |= 0x01;
    //    P6OUT |= 0x01;
    //    P6OUT &= ~0x01;
    //    __no_operation();
    //    __no_operation();
    //    for (f = 0; f < 0xFFFF; f++)
    //        {
    //            __no_operation();
    //            __no_operation();
    //            __no_operation();
    //        }
    //    P6OUT |= 0x01;


    P2DIR |= 0x01; //Shutdown 3v6 - Logic 0 on GPIO -> Power rail off
    //    P2OUT &= ~0x01;
    P2OUT |= 0x01;
    P2OUT &= ~0x01;
    P2OUT |= 0x01;

    P2DIR |= 0x20; //Shutdown Geo - Logic 1 on GPIO -> Power rail off
    P2OUT |= 0x20;
    P2OUT &= ~0x20;
    P2OUT |= 0x20;
    P2OUT &= ~0x20;

    ////////////////
    //Setup Pin 2.3 to control ResetBRO signal
    ////////////////
    P2DIR |= 0x08;
    P2OUT &= ~0x08;
    P2OUT |= 0x08;
    P2OUT &= ~0x08;
    P2OUT |= 0x08;

//////////////////////////////////////////

//////////////////////////////////////////
// I2C setup

#ifdef EPS_INTERNAL_I2C
    P4SEL |= 0x06;                            // Assign I2C pins to USCI_B1 (pins P4.2 and P4.1)
    UCB1CTL1 |= UCSWRST;                      // Hold USCI module in reset whilst we configure it
    UCB1CTL0 = UCMST + UCMODE_3 + UCSYNC;     // I2C Master, synchronous mode
    UCB1CTL1 = UCSSEL_2 + UCSWRST;            // Use SMCLK
    UCB1BR0 = 12;                             // fSCL = SMCLK/40 = 4MHz/40 = ~100kHz // was set to 12
    UCB1BR1 = 0;
    UCB1I2CSA = 0x48;                         //On EPS, 0x48 is the LTC2991
                                              //  later on when the i2c bus is accessed from different tasks, but it
                                              //  needs to be set to a valid slave address here in order to initialise
                                              //  the i2c bus correctly, so the temp sensor has been chosen.
                                              // i2c slave addresses: 0x48 is temp sensor, 0x68 is imu //0x69 is rtc
    UCB1CTL1 &= ~UCSWRST;                     // Clear SW reset, resume operation
    UCB1IE |= UCRXIE;                         // Enable RX interrupt
    UCB1IE |= UCTXIE + UCSTTIE + UCSTPIE;     // Enable TX interrupt


    // LTC2991 test code:
    char data1 = 0x0;
    char data2 = 0x0;


    i2cB1TXBuffer[0] = 0x08; //Control register
    i2cB1TXBuffer[1] = 0x00; //Single Shot mode       0x10; //Repeated acquisition mode
    i2cB1TXByteCtr = 2;
    perform_internal_i2c_write();

    i2cB1TXBuffer[0] = 0x06; //V1, V2 and V3, V4 Control register
    i2cB1TXBuffer[1] = 0x10; //Differential mode (V3 - V4)
    i2cB1TXByteCtr = 2;
    perform_internal_i2c_write();

    i2cB1TXBuffer[0] = 0x01; //Trigger register
    i2cB1TXBuffer[1] = 0xFF; //Any value can be written to the trigger register
    i2cB1TXByteCtr = 2;
    perform_internal_i2c_write();

    //measurement delay is 1.8 ms max, so a couple of delay loops used below
    int z;
    for (z = 0; z < 0xFFFF; z++)
    {
        __no_operation();
    }

    for (z = 0; z < 0xFFFF; z++)
    {
        __no_operation();
    }


    i2cB1TXBuffer[0] = 0x0E; //V3 MSB
    i2cB1TXByteCtr = 1;
    perform_internal_i2c_write();
    i2cB1RXBuffer[0] = 0x00; //reset rx buf so we can check contents in debugger after read occurrs
    i2cB1RXByteCtr = 1;
    perform_internal_i2c_read();
    receivedData[0] = i2cB1RXBuffer[0];

    i2cB1TXBuffer[0] = 0x0F; //V3 LSB
    i2cB1TXByteCtr = 1;
    perform_internal_i2c_write();
    i2cB1RXBuffer[0] = 0x00; //reset rx buf so we can check contents in debugger after read occurrs
    i2cB1RXByteCtr = 1;
    perform_internal_i2c_read();
    receivedData[1] = i2cB1RXBuffer[0];

    i2cB1TXBuffer[0] = 0x10; //V4 MSB
    i2cB1TXByteCtr = 1;
    perform_internal_i2c_write();
    i2cB1RXBuffer[0] = 0x00; //reset rx buf so we can check contents in debugger after read occurrs
    i2cB1RXByteCtr = 1;
    perform_internal_i2c_read();
    receivedData[2] = i2cB1RXBuffer[0];

    i2cB1TXBuffer[0] = 0x11; //V4 LSB
    i2cB1TXByteCtr = 1;
    perform_internal_i2c_write();
    i2cB1RXBuffer[0] = 0x00; //reset rx buf so we can check contents in debugger after read occurrs
    i2cB1RXByteCtr = 1;
    perform_internal_i2c_read();
    receivedData[3] = i2cB1RXBuffer[0];

    i2cB1TXBuffer[0] = 0x00;
    i2cB1TXByteCtr = 1;
    perform_internal_i2c_write();
    i2cB1RXBuffer[0] = 0x00; //reset rx buf so we can check contents in debugger after read occurrs
    i2cB1RXByteCtr = 1;
    perform_internal_i2c_read();
    data1 = i2cB1RXBuffer[0];
    int y;
    for (y = 0; y < 0xFFFF; y++)
    {
        __no_operation();
    }

#endif


#ifdef 0
    // INA3221 code
    char data1 = 0x0;
    char data2 = 0x0;
    i2cB1TXBuffer[0] = 0x01;
    i2cB1TXByteCtr = 3;
    perform_internal_i2c_write();
    i2cB1RXByteCtr = i2cB1TXBuffer[0] = 0x08; //Control register
    i2cB1TXBuffer[1] = 0x10; //Repeated acquisition mode
    i2cB1TXByteCtr = 2;
    perform_internal_i2c_write();
    perform_internal_i2c_read();
    data1 = i2cB1RXBuffer[0];
    data2 = i2cB1RXBuffer[1];
#endif


#ifdef EPS_EXTERNAL_I2C_MASTER

    P3SEL |= 0x03;                            // Assign I2C pins to USCI_B0 (pins P3.0 and P3.1)
    UCB0CTL1 |= UCSWRST;                      // Hold USCI module in reset whilst we configure it
    UCB0CTL0 = UCMST + UCMODE_3 + UCSYNC;     // I2C Master, synchronous mode
    UCB0CTL1 = UCSSEL_2 + UCSWRST;            // Use SMCLK
    UCB0BR0 = 12;                             // fSCL = SMCLK/40 = 4MHz/40 = ~100kHz // was set to 12
    UCB0BR1 = 0;
    UCB0I2CSA = 0x48;  //EPS external     // Set Slave Address is to 0x48 (temp sensor). Slave address is changed
                                              //  later on when the i2c bus is accessed from different tasks, but it
                                              //  needs to be set to a valid slave address here in order to initialise
                                              //  the i2c bus correctly, so the temp sensor has been chosen.
                                              // i2c slave addresses: 0x48 is temp sensor, 0x68 is imu //0x69 is rtc
    UCB0CTL1 &= ~UCSWRST;                     // Clear SW reset, resume operation
    UCB0IE |= UCRXIE;                         // Enable RX interrupt
    UCB0IE |= UCTXIE + UCSTTIE + UCSTPIE;     // Enable TX interrupt

#endif

#ifdef EPS_EXTERNAL_I2C_SLAVE

    P3SEL |= 0x03;                            // Assign I2C pins to USCI_B0
    UCB0CTL1 |= UCSWRST;                      // Enable SW reset
    UCB0CTL0 = UCMODE_3 + UCSYNC;             // I2C Slave, synchronous mode
    UCB0I2COA = 0x48;                         // Own Address is 048h
    UCB0CTL1 &= ~UCSWRST;                     // Clear SW reset, resume operation
    UCB0IE |= UCRXIE;                         // Enable RX interrupt


    //////////////////
    // Pin toggle setup
    //////////////////
    P6DIR |= 0x02;    // pin 6.1 (GPIO1)
    P6OUT |= 0x02;

    RXDataIndex = 0;

    __bis_SR_register(GIE);

#endif

    /* Control loop */
    while (1)
    {
        //////////////////
        // Pin toggle
        //////////////////
        P6OUT ^= 0x02;

        __no_operation();
    }

    return 0;
}
