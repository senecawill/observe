## Getting the Units on and updated.

Download QGIS preferably a LTR version.
Load it up and create a blank project.

in the "Browser" box on the left, right click empty area and click add connection.
Link to our database tables from senecainfo.

#### Add in layers:
WV_Unit_Boundaries_Raw from the WFST table

If a layer is checked on and you cant see, right click the layer and click zoom to layer.
If its far away the projection is wrong. Go to Project at the top left then go to properties.
Go to CRS tab and in filter search for WGS 84 / Pseudo-Mercator.
Then go to the Source tab for each layer that inst displaying right and change their source to the projection above.

#### Add Styling:
Right click the layer and click "properties" at the bottom.
Click "Labels" in the tab selection on the left side.
Where it says "No label" click it for a dropdown.
Click "Single Labels"
The "Value" field is what column is displayed as the label for the layer, make it unit
Click "Apply" to see changes without exiting the styling menu.

Now to change the shapes styling click the "Symbology" Tab.
click "simple fill" you might have to dropdown it from "Fill".
Edit color, stroke color, and width as see fit.
Go back to "Fill" when done to change to opacity to 50% or so to make it see through.

Now your layers should be added, styled, and editable.

Now to create a duplicate the unit layer to update it, if confident, update the layer directly.
Right click the Unit layer and click export then click save feature as. save it to a folder and make sure the format is ESRI Shapefile and the CRS field is the same as the current Unit layer.
Right now the CRS of Unit layers are EPSG:4326-WGS 84.

Now we need to delete every unit ON THE NEW LOCAL LAYER, click the unit layer to highlight it, click the edit button.
Find the Select features by area button in the bars at the top, then highlight the whole state to select every unit.
Now in the edit tools bar, click the trashcan to delete the units.
Now you can create polygon in the edit tools bar and start mapping units.
More detail how to map them, further below.

Once you mapped a batch and checked the fields you need to copy and paste the units to the live layer.
Using the select features tool like before, cover the state.
Then highlight the new units layer, toggle editing, and click copy features button in the edit tools bar.
Then highlight the units raw layer, toggle editing, and click paste features button in the edit tools bar.
delete the units on the local layer. then toggle editing, and save both layers.



## How to map units

To edit the new unit layer we use editing tools. Each layer has a set of tools at the top, starting with a pencil button and ending with 
