import os
import json
from dotenv import load_dotenv

import paho.mqtt.client as paho
from paho import mqtt
from InputTypes import NewPlayer
from game import Game
import time


game_over = False
suggestion_received = False

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
    print("\n mid: " + str(mid))


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
    print("\n Subscribed: " + str(mid) + " " + str(granted_qos) + "\n")


# print message, useful for checking if it was successful
def on_message(client, userdata, msg):
    """
        Prints a mqtt message to stdout ( used as callback for subscribe )
        :param client: the client itself
        :param userdata: userdata is set when initiating the client, here it is userdata=None
        :param msg: the message with topic and payload
    """

    global suggestion_received
    print("message: " + msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
    message_content = json.loads(msg.payload.decode())
    if "Game Over" in message_content:
        game_over = True
    elif 'suggestion' in message_content:
        print(f"Suggestion received: {message_content['suggestion']}")
        suggestion_received = True  # Set the flag when a suggestion is received



def get_user_direction(player, client, lobby_name, teammate_topic):
    global suggestion_received
    suggestion_received = False  # Ensure the flag is reset at the start of the function

    while True:
        print("\nOptions:")
        print("1. Move UP")
        print("2. Move DOWN")
        print("3. Move LEFT")
        print("4. Move RIGHT")
        print("5. Request move suggestion from teammate")
        user_input = input(f"\n What direction should {player} move in?   \n")
        
        directions = {1: "UP", 2: "DOWN", 3: "LEFT", 4: "RIGHT"}
        
        if int(user_input) == 5:
            print("Requesting suggestion...")
            
            user_suggestion = input("Provide a suggesed input from 1 to 4 as mentioned above")
            if int(user_suggestion) in [1,2,3,4]: 
                suggestion_received = True 
                            
                client.publish(teammate_topic, json.dumps({'request': int(user_suggestion), 'from': player}))
                client.subscribe(teammate_topic.replace('request', 'response'))
            
            # Wait for suggestion or timeout
            start_time = time.time()
            timeout = 5  # seconds
            while time.time() - start_time < timeout and not suggestion_received:
                time.sleep(1)
            if suggestion_received:
                print(f"Suggestion received, the suggested move is {user_suggestion} \n")
                suggestion_received = False  # Reset the flag
            else:
                print("Teammate does not care. Please choose your move.")
        else:
            dir = directions.get(int(user_input))
            if dir:
                return dir
            else:
                print("Invalid input, please try again.")

    
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
    #client.on_subscribe = on_subscribe # Can comment out to not print when subscribing to new topics
    client.on_message = on_message
    #client.on_publish = on_publish # Can comment out to not print when publishing to topics

    lobby_name = "TestLobby"
    player_1 = "tom"
    player_2 = "dick"
    player_3 = "harry"
    player_4 = "johnson"
    #test_pla = NewPlayer(lobby_name=lobby_name, team_name= "test_team", player_name="taimur")
    
    lobby_name = input("What is the lobby name? \n")
    

    client.subscribe(f'games/{lobby_name}/+/game_state')
    client.subscribe(f'games/{lobby_name}/scores')
     
    player_count = input("what is the player count? \n")
    
    for i in range(int(player_count)): 
        player, team = get_player_names()
        client.publish(topic = "new_game", payload = json.dumps({'lobby_name':lobby_name,
                                            'team_name':team,
                                            'player_name' : player}))

    time.sleep(5) # Wait a second to resolve game start
    client.publish(f"games/{lobby_name}/start", "START")
    client.loop_start()
    
    while not game_over:
        # Player 1's turn
        move = get_user_direction(player_1, client, lobby_name, f"games/{lobby_name}/{player_2}/request")
        if move:
            client.publish(f"games/{lobby_name}/{player_1}/move", move)
        #print(game.map)

        # Player 2
        move = get_user_direction(player_2, client, lobby_name, f"games/{lobby_name}/{player_1}/request")
        if move:
            client.publish(f"games/{lobby_name}/{player_2}/move", move)

       #print(game.map)

        # Player 4
        move = get_user_direction(player_3, client, lobby_name, f"games/{lobby_name}/{player_4}/request")
        if move:
            client.publish(f"games/{lobby_name}/{player_3}/move", move)
        #print(game.map)
        
        # Player 4
        move = get_user_direction(player_4, client, lobby_name, f"games/{lobby_name}/{player_3}/request")
        if move:
            client.publish(f"games/{lobby_name}/{player_4}/move", move)
        #print(game.map)

    print("YOUR TIME IS UP HAHAHAHAHA \n")
    client.publish(f"games/{lobby_name}/start", "STOP")