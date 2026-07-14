# rose-game-engine
[ROSE game](https://github.com/RedHat-Israel/ROSE) game engine.

This component implement the ROSE game logic, and road simulation.

<p align="center">
  <img src="engine.png" alt="rose game components diagram" width="400"/>
</p>

ROSE project: https://github.com/RedHat-Israel/ROSE

## Requirements

 Requires | Version | |
----------|---------| ---- |
 Podman (or Docker) | >= 4.8 | For running containerized |
 PYthon   | >= 3.9  | For running the code loally |

## ROSE game components

Component | Reference |
----------|-----------|
Game engine | https://github.com/RedHat-Israel/rose-game-engine |
Game web based user interface | https://github.com/RedHat-Israel/rose-game-web-ui |
Self driving car module | https://github.com/RedHat-Israel/rose-game-ai |
Self driving car module example | https://github.com/RedHat-Israel/rose-game-ai-reference |

## Running the game engine locally

Clone this repository.

Run the engine locally:

```bash
# Install requirements
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run the game engine server
python main.py
```

## Running ROSE game on kubernetes cluster

Log into your cluster, and apply the game inventory.
The game user interface will be avaliable on `NodePort` service `rose/rose-game-web-ui`


```bash
# Apply the game inventory
kubectl apply -f https://raw.githubusercontent.com/RedHat-Israel/rose-game-engine/main/rose-game.yaml

# Get the user interface node port
kubectl get svc -n rose rose-game-web-ui

# On openshift expose the user interface route
#oc expose svc/rose-game-web-ui -n rose --port=8080

# Car driving modules will be available using internal service URL
# module intrenal URL example: http://rose-game-ai-reference.rose.svc.cluster.local:8081
```

## Running ROSE game components containerized

### Running the game engine ( on http://127.0.0.1:8880 )

``` bash
podman run --rm --network host -it quay.io/rose/rose-game-engine:latest
```

### Running the game web based user interface ( on http://127.0.0.1:8080 )

``` bash
podman run --rm --network host -it quay.io/rose/rose-game-web-ui:latest
```

### Running community contributed driver ( on http://127.0.0.1:8082 )

You can use community drivers to compare and evaluate your driver during the development process.

``` bash
podman run --rm --network host -it quay.io/yaacov/rose-go-driver:latest --port 8082
```

### Running your self driving module, requires a local `mydriver.py` file with your driving module. ( on http://127.0.0.1:8081 )

``` bash
# NOTE: will mount mydriver.py from local directory into the container file system
podman run --rm --network host -it \
  -v $(pwd)/:/driver:z \
  -e DRIVER=/driver/mydriver.py \
  -e PORT=8081 \
  quay.io/rose/rose-game-ai:latest
```

### Testing your driver

Send `car` and `track` information by uring `POST` request to your driver ( running on http://127.0.0.1:8081 ):

``` bash
curl -X POST -H "Content-Type: application/json" -d '{
            "info": {
                "car": {
                    "x": 3,
                    "y": 8
                }
            },
            "track": [
                ["", "", "bike", "", "", ""],
                ["", "crack", "", "", "trash", ""],
                ["", "", "penguin", "", "", "water"],
                ["", "water", "", "trash", "", ""],
                ["barrier", "", "", "", "bike", ""],
                ["", "", "trash", "", "", ""],
                ["", "crack", "", "", "", "bike"],
                ["", "", "", "penguin", "water", ""],
                ["", "", "bike", "", "", ""]
            ]
        }' http://localhost:8081/
```

The response in `JSON` format should include the car name and the recommended action:

``` json
{
  "info": {
    "name": "Go Cart",
    "action": "pickup"
  }
}
```
