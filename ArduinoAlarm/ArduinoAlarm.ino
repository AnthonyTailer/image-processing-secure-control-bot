const int ledAzul = 4;
const int ledVerde = 3;     
const int ledVermelho = 2;
const int sensorPIR = 7;
const int buzzer = 8;

int alerta;

void setup() 
{
    pinMode(buzzer,OUTPUT);
    pinMode(sensorPIR, INPUT); 
    pinMode(ledAzul,OUTPUT); 
    pinMode(ledVerde,OUTPUT); 
    pinMode(ledVermelho,OUTPUT);   
    Serial.begin(9600); 
}

void tocaAlarme()
{
    // Aciona o buzzer na frequencia relativa ao Dó em Hz
    tone(buzzer,261, 500);    
    delay(200);
    noTone(buzzer); 
    tone(buzzer,392, 500);// Aciona o buzzer na frequencia relativa ao SOL em Hz          
    delay(200);
    noTone(buzzer); 
}

void acionaLed()
{
  //Acendendo cada cor individualmente.  
  digitalWrite(ledAzul,HIGH);
  delay(500);
  digitalWrite(ledAzul,LOW);
  tocaAlarme();
   
  digitalWrite(ledVerde,HIGH);
  delay(500);
  digitalWrite(ledVerde,LOW);
   tocaAlarme();
   
  digitalWrite(ledVermelho,HIGH);
  delay(500);
  digitalWrite(ledVermelho,LOW);
   tocaAlarme();    
   
  //Misturando as cores do led para obter cores diferentes.
  digitalWrite(ledAzul,HIGH);     
  digitalWrite(ledVerde,HIGH);
  digitalWrite(ledVermelho,HIGH);
  delay(500);     
  tocaAlarme();
  digitalWrite(ledAzul,HIGH);
  digitalWrite(ledVerde,HIGH);
  digitalWrite(ledVermelho,LOW);  
  delay(500);      
  tocaAlarme();
  digitalWrite(ledAzul,LOW);
  digitalWrite(ledVerde,HIGH);
  digitalWrite(ledVermelho,HIGH);
  delay(500);      
  tocaAlarme();
  digitalWrite(ledAzul,HIGH);
  digitalWrite(ledVerde,LOW);
  digitalWrite(ledVermelho,HIGH);
  delay(500);
  tocaAlarme();
}

void loop() 
{
  alerta = digitalRead(sensorPIR);
  //Serial.println(alerta);
  
  if (alerta == HIGH){
    Serial.println(1);
    tocaAlarme();
    acionaLed();
  }else{
    noTone(buzzer); 
    digitalWrite(ledAzul,LOW);
    digitalWrite(ledVerde,LOW);
    digitalWrite(ledVermelho,LOW);
  }
    
}
