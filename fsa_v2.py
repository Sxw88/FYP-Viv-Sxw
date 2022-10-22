from __future__ import annotations
from abc import ABC, abstractmethod
import time

next_step = "non"

# The Finite State Automata (FSA) class is the context. It should be initiated with a default state.
class FSA:

    _state = None

    def __init__(self, state: State) -> None:
        self.setFSA(state)

    # method to change the state of the object
    def setFSA(self, state: State):

        self._state = state
        self._state.fsa = self

    def presentState(self):
        print(f"[ Currently in State: {type(self._state).__name__} ]")

    # the methods for executing the Finite State Machine's functionality.
    # These depends on the current state of the object.
    def startInitAnchoring(self):
        self._state.startInitAnchoring()

    def startLocalization(self):
        self._state.startLocalization()

    def startTTE(self): # Travel-to-Edge state
        self._state.startTTE()

    def startTriangulation(self):
        self._state.startTriangulation()

    def startAnchored(self):
        self._state.startAnchored()



# The common state interface for all the states
class State(ABC):
    @property
    def fsa(self) -> FSA:
        return self._fsa

    @fsa.setter
    def fsa(self, fsa: FSA) -> None:
        self._fsa = fsa

    @abstractmethod
    def startInitAnchoring(self) -> None:
        pass

    @abstractmethod
    def startLocalization(self) -> None:
        pass

    @abstractmethod
    def startTTE(self) -> None:
        pass

    @abstractmethod
    def startTriangulation(self) -> None:
        pass

    @abstractmethod
    def startAnchored(self) -> None:
        pass
    

# The concrete states
# Six total states: Initialisation, Init-Anchoring, Localization,
# Travel-to-Edge (TTE), Triangulation, and Anchored

class Initialisation(State):

    def __init__(self):
        print("Initialising ...")
        # Main code for Initialisation goes here
        global next_step
        next_step = "i-a"
    
    # The robot starts to anchor itself if no other reference points can be found
    def startInitAnchoring(self) -> None:
        print("Robot is entering Anchoring state.")
        time.sleep(0.3)
        print("*")
        time.sleep(0.3)
        print("*")
        self.fsa.setFSA(InitAnchoring())

    # The robot enters Localization state if >2 reference points are found
    def startLocalization(self) -> None:
        print("Robot is entering Localization state.")
        time.sleep(0.3)
        print("*")
        time.sleep(0.3)
        print("*")
        self.fsa.setFSA(Localization())

    # Irrelevant states
    def startTTE(self) -> None:
        print("WARNING: No actions will be carried out")

    def startTriangulation(self) -> None:
        print("WARNING: No actions will be carried out")

    def startAnchored(self) -> None:
        print("WARNING: No actions will be carried out")



class InitAnchoring(State):

    def __init__(self):
        print("Anchoring ...")
        # Main code for Initialization-Anchoring process goes here
        global next_step
        next_step = "anc"

    # Proceeds to Anchored state 
    def startAnchored(self) -> None:
        print("Robot is entering Anchored state.")
        time.sleep(0.3)
        print("*")
        time.sleep(0.3)
        print("*")
        self.fsa.setFSA(Anchored())
    
    # Irrelevant states
    def startInitAnchoring(self) -> None:
        print("WARNING: No actions will be carried out")

    def startLocalization(self) -> None:
        print("WARNING: No actions will be carried out")
    
    def startTTE(self) -> None:
        print("WARNING: No actions will be carried out")

    def startTriangulation(self) -> None:
        print("WARNING: No actions will be carried out")



class Localization(State):

    def __init__(self):
        print("Localizing ...")
        # main code for Localization goes here
        global next_step
        next_step = "tte"
    
    # Travel-to-Edge if needed
    def startTTE(self) -> None:
        print("Robot is entering Travel-to-Edge state.")
        time.sleep(0.3)
        print("*")
        time.sleep(0.3)
        print("*")
        self.fsa.setFSA(TTE())
    
    # Enters Triangulation state if no TTE needed
    def startTriangulation(self) -> None:
        print("Robot is entering Triangulation state.")
        time.sleep(0.3)
        print("*")
        time.sleep(0.3)
        print("*")
        self.fsa.setFSA(Triangulation())

    # Irrelevant states
    def startInitAnchoring(self) -> None:
        print("WARNING: No actions will be carried out")

    def startLocalization(self) -> None:
        print("WARNING: No actions will be carried out")

    def startAnchored(self) -> None:
        print("WARNING: No actions will be carried out")



class TTE(State):

    def __init__(self):
        print("Attempting Travel-to-Edge ...")
        # Main code for Travelling-to-Edge process goes here
        global next_step
        next_step = "tri"

    # Enters Triangulation state if TTE successful
    def startTriangulation(self) -> None:
        print("Robot is entering Triangulation state.")
        time.sleep(0.3)
        print("*")
        time.sleep(0.3)
        print("*")
        self.fsa.setFSA(Triangulation())

    # Enters Localization state if TTE is NOT successful
    def startLocalization(self) -> None:
        print("Robot is entering Localization state.")
        time.sleep(0.3)
        print("*")
        time.sleep(0.3)
        print("*")
        self.fsa.setFSA(Localization())

    # Irrelevant states
    def startInitAnchoring(self) -> None:
        print("WARNING: No actions will be carried out")

    def startTTE(self) -> None:
        print("WARNING: No actions will be carried out")

    def startAnchored(self) -> None:
        print("WARNING: No actions will be carried out")
    


class Triangulation(State):

    def __init__(self):
        print("Triangulating...")
        # Main code for Triangulation process goes here
        global next_step
        next_step = "anc"

    # Enters Localization state if Triangulation is NOT successful
    def startLocalization(self) -> None:
        print("Robot is entering Localization state.")
        time.sleep(0.3)
        print("*")
        time.sleep(0.3)
        print("*")
        self.fsa.setFSA(Localization())

    # Proceeds to Anchored stateif Triangulation is successful
    def startAnchored(self) -> None:
        print("Robot is entering Anchored state.")
        time.sleep(0.3)
        print("*")
        time.sleep(0.3)
        print("*")
        self.fsa.setFSA(Anchored())
    
    # Irrelevant states
    def startInitAnchoring(self) -> None:
        print("WARNING: No actions will be carried out")

    def startTTE(self) -> None:
        print("WARNING: No actions will be carried out")

    def startTriangulation(self) -> None:
        print("WARNING: No actions will be carried out")
        


class Anchored(State):

    def __init__(self):
        print("Robot has successfully entered the Anchored state.")
        # Code for Anchored state goes here
        print("[*] Robot currently Anchored")
        time.sleep(3)

    def startAnchored(self) -> None:
        print("[*] Robot currently Anchored")
        time.sleep(3)

    # Irrelevant states
    def startInitAnchoring(self) -> None:
        print("WARNING: No actions will be carried out")

    def startTTE(self) -> None:
        print("WARNING: No actions will be carried out")

    def startTriangulation(self) -> None:
        print("WARNING: No actions will be carried out")

    def startLocalization(self) -> None:
        print("WARNING: No actions will be carried out")



def startFSA():
    global next_step

    # Initialise robot object
    myRobot = FSA(Initialisation())
    myRobot.presentState()

    while 1 == 1: 
        if next_step == "i-a":
            myRobot.startInitAnchoring()
        elif next_step == "lcl":
            myRobot.startLocalization()
        elif next_step == "tte":
            myRobot.startTTE()
        elif next_step == "tri":
            myRobot.startTriangulation()
        elif next_step == "anc":
            myRobot.startAnchored()
        
        myRobot.presentState()


if __name__ == "__main__":
    # The client code.

    startFSA()



"""


                   ┌───────────────────┐
                   │                   │
                   │                   │
                   │ Initial-Anchoring ├──────────────────────────────────────────────┐
                   │                   │                                              │
                   │                   │                                              │
                   └─────────▲─────────┘                                              │
                             │                                                        │
                             │                                                        │
                             │                                                        │
                             │                                                        │
                             │                                                        │
                             │                                                        │
                             │                                                        │
                   ┌─────────┴─────────┐                                    ┌─────────▼─────────┐
                   │                   │                                    │                   │
                   │                   │                                    │                   │
    ──────────────►│  Initialisation   │                                    │      Anchored     │
                   │                   │                                    │                   │
                   │                   │                                    │                   │
                   └─────────┬─────────┘                                    └─────────▲─────────┘
                             │                                                        │
                             │                                                        │
                             │                                                        │
                             │                                                        │
                             │                                                        │
                             │                                                        │
                             │                                                        │
                   ┌─────────▼─────────┐                               ┌──────────────┴─────┐
                   │                   │                               │                    │
                   │                   │                               │                    │
                   │   Localization    ◄───────────────────────────────►    Triangulation   │
                   │                   │                               │                    │
                   │                   │                               │                    │
                   └─────────▲─────────┘                               └──────────▲─────────┘
                             │                                                    │
                             │                                                    │
                             │                                                    │
                             │               ┌────────────────────────┐           │
                             │               │                        │           │
                             │               │                        │           │
                             └───────────────►     Travel-to-Edge     ├───────────┘
                                             │                        │
                                             │                        │
                                             └────────────────────────┘

"""
