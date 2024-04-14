import os
import json
from dotenv import load_dotenv

import paho.mqtt.client as paho
from paho import mqtt
from InputTypes import NewPlayer
import time

game_over = False

# setting callbacks for different events to see if it works, print the message etc.
def on_connect(client, userdata, flags, rc, properties=None):
    """
        Prints the result of the connection with a reasoncode to stdout ( used as callback for connect )
        :param client: the client itself
        :param userdata: userdata is set when initiating the client, here it is userdata=None
        :param flags: these are response flags sent by the broker
        :param rc: stands for reasonCode, which is a code for the connection result
        :param properties: can be used in MQTTv5, but is optional
    """
    print("CONNACK received with code %s." % rc)


# with this callback you can see if your publish was successful
def on_publish(client, userdata, mid, properties=None):
    """
        Prints mid to stdout to reassure a successful publish ( used as callback for publish )
        :param client: the client itself
        :param userdata: userdata is set when initiating the client, here it is userdata=None
        :param mid: variable returned from the corresponding publish() call, to allow outgoing messages to be tracked
        :param properties: can be used in MQTTv5, but is optional
    """
    print("mid: " + str(mid))


# print which topic was subscribed to
def on_subscribe(client, userdata, mid, granted_qos, properties=None):
    """
        Prints a reassurance for successfully subscribing
        :param client: the client itself
        :param userdata: userdata is set when initiating the client, here it is userdata=None
        :param mid: variable returned from the corresponding publish() call, to allow outgoing messages to be tracked
        :param granted_qos: this is the qos that you declare when subscribing, use the same one for publishing
        :param properties: can be used in MQTTv5, but is optional
    """
    print("Subscribed: " + str(mid) + " " + str(granted_qos))


# print message, useful for checking if it was successful
def on_message(client, userdata, msg):
    """
        Prints a mqtt message to stdout ( used as callback for subscribe )
        :param client: the client itself
        :param userdata: userdata is set when initiating the client, here it is userdata=None
        :param msg: the message with topic and payload
    """

    print("message: " + msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
    if "Game Over: " in str(msg.payload): 
        game_over = True



def get_user_direction(player) -> str: 
    user_input = input(f"what direction should {player} move in?   \n")
    directions  = {1: "UP", 2: "DOWN", 3: "LEFT", 4: "RIGHT"}
    dir = directions.get(int(user_input))
    return dir
    
    
def get_player_names() -> tuple:
    player = input("What is your name? \n")
    team = input("what is your team? \n")
    return (player, team)

if __name__ == '__main__':
    load_dotenv(dotenv_path='./credentials.env')
    
    broker_address = os.getenv('BROKER_ADDRESS')
    broker_port = int(os.getenv('BROKER_PORT'))
    username = os.getenv('USER_NAME')
    password = os.getenv('PASSWORD')

    client = paho.Client(callback_api_version=paho.CallbackAPIVersion.VERSION1, client_id="Player1", userdata=None, protocol=paho.MQTTv5)
    
    # enable TLS for secure connection
    client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
    # set username and password
    client.username_pw_set(username, password)
    # connect to HiveMQ Cloud on port 8883 (default for MQTT)
    client.connect(broker_address, broker_port)

    # setting callbacks, use separate functions like above for better visibility
    client.on_subscribe = on_subscribe # Can comment out to not print when subscribing to new topics
    client.on_message = on_message
    client.on_publish = on_publish # Can comment out to not print when publishing to topics

    lobby_name = "TestLobby"
    player_1 = "faraz"
    player_2 = "taimur"
    player_3 = "hamza"
    #test_pla = NewPlayer(lobby_name=lobby_name, team_name= "test_team", player_name="taimur")
    
    lobby_name = input("What is the lobby name? ")
    

    client.subscribe(f'games/{lobby_name}/+/game_state')
    client.subscribe(f'games/{lobby_name}/scores')
     
    player_count = input("what is the player count? \n")
    
    for i in range(int(player_count)): 
        player, team = get_player_names()
        client.publish(topic = "new_game", payload = json.dumps({'lobby_name':lobby_name,
                                            'team_name':team,
                                            'player_name' : player}))

    time.sleep(1) # Wait a second to resolve game start
    client.publish(f"games/{lobby_name}/start", "START")
    
    client.loop_start()
    
    while not game_over:
    
        client.publish(f"games/{lobby_name}/{player_1}/move", get_user_direction(player_1))
        client.publish(f"games/{lobby_name}/{player_2}/move", get_user_direction(player_2))
        client.publish(f"games/{lobby_name}/{player_3}/move", get_user_direction(player_3))
        

    print("YOUR TIME IS UP HAHAHAHAHA")
    client.publish(f"games/{lobby_name}/start", "STOP")