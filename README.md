# socket-transit-file-and-message
send and receive message and file by python socket.

You could use a sample cli tool on it, could also invoke the methods in your project.

Could you please click :star: if my code help you?

## Usage:

### Configuration
    You should modify config.json.
   * local_ip: Your local address IP. (**essential && important**)
   * receive_port: Config the ports to receive files or messages.You must make sure that the receiver and sender have configed same ports.
   * save_position: The position you want to save the files to.
***
### Cli Usage

#### Help
    help                      get help message.
#### Receive
    This program could receive message and file automatically.
#### Send a message
    send <ip> -m <message>    send a message to target IP
#### Send a file
    send <ip> -f <filename>   send a file to target IP
#### quit
    quit                      quit this program safety
    