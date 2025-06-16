import os
import logging


def makePOSfileFromRINEX(roverObservables, baseObservables, navFile, outfname, executablePath="C:/RTKLIB/bin/rnx2rtkp.exe", configFile="C:/Users/pfloyd/Documents/GitHub/FRF---Task-1/rtklib.conf",**kwargs):
    """Runs rnx2rtkp using an absolute path from the Downloads folder."""
    #sp3 = kwargs.get("sp3", "")
    #freq = kwargs.get("freq", 3)

    logging.debug(f"Converting {os.path.basename(roverObservables)} using RTKLIB")

    os.system(
        f"{executablePath} -o {outfname} -t -k {configFile} {roverObservables} {baseObservables} {navFile}"
    )


# Change path to your location
roverObservables = "C:/Users/pfloyd/Documents/GitHub/FRF---Task-1/Rover.24O"
baseObservables = "C:/Users/pfloyd/Documents/GitHub/FRF---Task-1/Base.24o"
navFile = "C:/Users/pfloyd/Documents/GitHub/FRF---Task-1/Nav.24n"
outfname =  "C:/Users/pfloyd/Documents/GitHub/FRF---Task-1/528rtk.pos"

# Create POS Fle
makePOSfileFromRINEX(roverObservables,baseObservables,navFile, outfname,executablePath="C:/RTKLIB/bin/rnx2rtkp.exe",configFile="C:/Users/pfloyd/Documents/GitHub/FRF---Task-1/rtklib.conf")