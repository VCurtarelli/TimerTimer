// the setup routine runs once when you press reset:
void setup() {
  // initialize serial communication at 9600 bits per second:
  Serial.begin(9600);
  for (int i = 2; i < 10; i++)
  {
    pinMode(i, INPUT);
  }
}

int v_A0;
int v_A1;
int v_A2;
int v_A3;
int v_A4;
int v_A5;
int v_A6;
int v_A7;

int v_D0;
int v_D1;
int v_D2;
int v_D3;
int v_D4;
int v_D5;
int v_D6;
int v_D7;

boolean command = true;
// the loop routine runs over and over again forever:
void loop() {
  v_A0 = analogRead(A0);
  v_A1 = analogRead(A1);
  v_A2 = analogRead(A2);
  v_A3 = analogRead(A3);
  v_A4 = analogRead(A4);
  v_A5 = analogRead(A5);
  v_A6 = analogRead(A6);
  v_A7 = analogRead(A7);

  v_D0 = digitalRead(2);
  v_D1 = digitalRead(3);
  v_D2 = digitalRead(4);
  v_D3 = digitalRead(5);
  v_D4 = digitalRead(6);
  v_D5 = digitalRead(7);
  v_D6 = digitalRead(8);
  v_D7 = digitalRead(9);

  // send COMMAND through the Serial prot
  if (command == true)
  {
    command = false;
    Serial.print("command ");
    Serial.print(v_D7);
    Serial.print(" ");
    Serial.print(v_D6);
    Serial.print(" ");
    Serial.print(v_D5);
    Serial.print(" ");
    Serial.print(v_D4);
    Serial.print(" ");
    Serial.print(v_D3);
    Serial.print(" ");
    Serial.print(v_D2);
    Serial.print(" ");
    Serial.print(v_D1);
    Serial.print(" ");
    Serial.print(v_D0);
    Serial.println();
  }

  // send DATA through the Serial port
  else if (command == false)
  {
    command = true;
    Serial.print("data ");
    Serial.print(v_A0);
    Serial.print(" ");
    Serial.print(v_A1);
    Serial.print(" ");
    Serial.print(v_A2);
    Serial.print(" ");
    Serial.print(v_A3);
    Serial.print(" ");
    Serial.print(v_A4);
    Serial.print(" ");
    Serial.print(v_A5);
    Serial.print(" ");
    Serial.print(v_A6);
    Serial.print(" ");
    Serial.print(v_A7);
    Serial.println();
  }
  delay(25);        // delay in between reads for stability
}
