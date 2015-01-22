// Test functions for libComedi Elevator control. Connects all buttons and
// lights. Can be used for testing an elevator, or as an example of use of the
// drivers.
//
// 2008 Martin Korsgaard

#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <assert.h>
#include <unistd.h>
#include <signal.h>
#include <time.h>
#include <unistd.h>
#include <string.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netdb.h> 
#include<arpa/inet.h> //inet_addr
#include<pthread.h>//makefile?????????????????????????????????
#include<semaphore.h>

#include "elev.h"
int speed=75;
int floornow;
int a;
int b;
int c;
bool stop = 0;
static int matrise[3][4] = {{0}};
bool obst;
int sock;
bool opp=0;
char message[256];
bool list[4] = {1,0,0,0};


void error(const char *msg)
{
    perror(msg);
    exit(0);
}

// Callback function that handles the elevator reaching a floor
static void signal_floor_sensor(int floor, int value)
{
    elev_set_floor_indicator(floor);
	floornow = floor;
	
	matrise[0][floor] = 0;
	matrise[1][floor] = 0;
	matrise[2][floor] = 0;
	elev_set_button_lamp(0, floornow, matrise[0][floornow]);
	elev_set_button_lamp(1, floornow, matrise[1][floornow]);
	elev_set_button_lamp(2, floornow, matrise[2][floornow]);

if (floor ==0 && opp){
	send(sock,"floor 1 up \n",strlen("floor 1 up \n"), 0);
}
if (floor ==1 && opp){
	send(sock,"floor 2 up \n",strlen("floor 2 up \n"), 0);
		}
if (floor ==2 && opp){
	send(sock,"floor 3 up \n",strlen("floor 3 up \n"), 0);}
if (floor == 3 && !opp){
	send(sock,"floor 4 down \n",strlen("floor 4 down \n"), 0);
}

if (floor == 2 && !opp){
	send(sock,"floor 3 down \n",strlen("floor 3 down \n"), 0);
}
if (floor ==1 && !opp){
	send(sock,"floor 2 down \n",strlen("floor 2 down \n"), 0);
}
    //if (floor == 0) 
		//elev_set_speed(1000);
    //else if (floor == 3)
		//elev_set_speed(-1000);

    printf(__FILE__ ": Floor %d %s.\n", floor+1, value ? "arrive" : "depart");
}


void *motta(void *arg){
while(1){
recv(sock,message,255,0);
c = message[0] - '0';
list[c-1]=1;
}
return 0;
}


// Callback for elevator buttons being pushed.
static void signal_button_pushed(int floor, int dir)	//denne funksjonen må brukes til å fikse problemet med knappene(antar jeg...)
{
    //matrise[3][4] = {{0}};

    matrise[dir][floor] = 1;				//regned med denne linje, og denne fuknsjonen kan løse alle problemer!
	elev_set_button_lamp(dir, floor, matrise[dir][floor]);




if (matrise[0][0]){
	send(sock,"button 1 up \n",strlen("button 1 up \n"), 0);
}
if (matrise[0][1]){
	send(sock,"button 2 up \n",strlen("button 2 up \n"), 0);
		}
if (matrise[0][2]){
	send(sock,"button 3 up \n",strlen("button 3 up \n"), 0);}
if (matrise[1][1]){
	send(sock,"button 2 down \n",strlen("button 2 down \n"), 0);
}

if (matrise[1][2]){
	send(sock,"button 3 down \n",strlen("button 3 down \n"), 0);
}
if (matrise[1][3]){
	send(sock,"button 4 down \n",strlen("button 4 down \n"), 0);
}


//??


	printf(__FILE__ ": Button %s pushed for floor %d.\n", dir==0?"CALL UP":dir==1?"CALL DOWN":"COMMAND", floor+1);
}



// Callback for stop.
static void signal_stop(int dummy, int dummy2)
{
    static int lamp = 0;
    lamp ^= 1;
	stop = !stop;
	elev_set_stop_lamp(lamp);
	printf(__FILE__ ": Stop button pushed!\n");
}



// Callback for obstruction. Sets the stop lamp.
static void signal_obstruction(int dummy, int value)
{
    elev_set_door_open_lamp(value);
	obst = value;
	printf(__FILE__ ": Obstruction switch flipped!\n");

}


void ctrlc(int x)
{
    elev_set_speed(0);
	//send(sock,"Control c ble trykket\n",strlen("Control c ble trykket\n"));				// skriv noe her!
    exit(0);
        close(sock);
}

int main()
{
	 //Initialize hardware
	if (!elev_init()) {
		printf(__FILE__ ": Unable to initialize elevator hardware.\n");
		exit (1);
	}
	
signal(SIGINT, ctrlc);
    
    //chatprogramm
    
struct sockaddr_in server;
message[1000] = "floor 1 idle";

//Create socket
sock = socket(AF_INET , SOCK_STREAM , 0);
if (sock == -1)
{
printf("Could not create socket");
}
puts("Socket created");

server.sin_addr.s_addr = inet_addr("129.241.187.141");
server.sin_family = AF_INET;
server.sin_port = htons( 10000 );

//Connect to remote server
if (connect(sock , (struct sockaddr *)&server , sizeof(server)) < 0)
{
perror("connect failed. Error");
return 1;
}

puts("Connected\n");

 
    //Chatslutt
    pthread_t pth;
    pthread_create(&pth, NULL, motta, &floornow);
   
    
        signal(SIGINT, ctrlc);

	elev_register_callback(SIGNAL_TYPE_CALL_UP, &signal_button_pushed);
	elev_register_callback(SIGNAL_TYPE_CALL_DOWN, &signal_button_pushed);
	elev_register_callback(SIGNAL_TYPE_COMMAND, &signal_button_pushed);
	elev_register_callback(SIGNAL_TYPE_SENSOR, &signal_floor_sensor);
	elev_register_callback(SIGNAL_TYPE_STOP, &signal_stop);
	elev_register_callback(SIGNAL_TYPE_OBSTR, &signal_obstruction);
	elev_reset_all_lamps();
			// antall heiser
			// Må kjøre på flere program, et program for hver heis? Kordan skal det foregå?
			

	send(sock,"floor 1 idle \n",strlen("floor 1 idle \n"), 0);
	bzero(message, 256);
     //read(sock, message, 256);

	

	elev_set_speed(-speed);
	elev_enable_callbacks();
	floornow = 2;
printf ("%d\n",floornow);
	while (1){
		printf ("Floornow %d\n",floornow);
		printf ("list= %d%d%d%d \n",list[0],list[1],list[2],list[3]);
		if (stop || obst){			//stopper om du har trykket på stoppknappen, eller forstyrret heisen.
		printf ("stop\n");
		//send(sock,"Nå stoppet heisen\n",strlen("Nå stoppet heisen\n"));
		elev_set_speed(0);
		while (stop|| obst);
		}		
		else if (list[floornow]==1){
		printf ("du har nådd rett etasje\n");
	    	elev_set_speed(0);
		elev_set_door_open_lamp(1);
		sleep(1);			//Åpne dør!
		elev_set_door_open_lamp(0);
		list[floornow]=0;
		printf ("%d\n",list[floornow]);
		



if (floornow==0){
	send(sock,"floor 1 idle \n",strlen("floor 1 idle \n"), 0);
}
if (floornow==1){
	send(sock,"floor 2 idle \n",strlen("floor 2 idle \n"), 0);
		}
if (floornow ==2){
	send(sock,"floor 3 idle \n",strlen("floor 3 idle \n"), 0);}
if (floornow ==3){
	send(sock,"floor 4 idle \n",strlen("floor 4 idle \n"), 0);
}


		
		}
		

		else{
		a = 0;
			if (opp){
			printf ("opp\n");
				for (int i = floornow; i < 4; i++){
				printf ("i=%d",i);
				printf ("  list[i]=%d\n",list[i]);
				if (list[i]==1){
				printf("Endrer hastigheten\n");
					elev_set_speed(speed);
					a +=1;
				}}
			}
			else if (!opp){
				printf ("ned\n");
				for (int i = floornow; i > -1; i--){
				printf ("i=%d",i);
				printf ("  list[i]=%d\n",list[i]);
				if (list[i]==1){
					elev_set_speed(-speed);
					a+=1;}}}}
if (a==0)
	opp = !opp;


for (int aa = 0; aa < 4; aa++){
if	(matrise[2][aa]==1){
		list[aa] =1;
		matrise[2][aa]=0;}}
		




//sleep(1);
	

	} ;

	

	return 0;
}


	// Heisen tar imot bestillinger, stopper når det ikke er noen bestillinger, Stopper ved stoppknapp. Knapper som lyser er problemet nå.
	// Lysene skal skru seg av når man kommer til etasjen, og skru seg på når du trykker på knappen.




