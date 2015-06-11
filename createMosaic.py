# Creating image mosaic, adding raster dataset, and populating required fields
# Global Agriclimate project
# Haitao Wang | April 2, 2015
# Update June 09, 2015

import arcpy, arceditor, csv
from arcpy import env
from compiler.pyassem import DONE

env.workspace = "//storage.vt.edu/gisdata/ArcGISServerData/cgit/Agroclimate/DataForPublish/WorldAgoData.gdb"
rasterTable = "//storage.vt.edu/gisdata/ArcGISServerData/cgit/Agroclimate/DataForPublish/pyCreateMosaic/rasList.csv"
agroMosaic = "agroclimate"

Proj = "GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]];-400 -400 1000000000;-100000 10000;-100000 10000;8.98315284119522E-09;0.001;0.001;IsHighPrecision" 

# Fields for Landscape Modeler web application
fields = [
             ["Name", "TEXT", 256, "Name"], 
             ["Title", "TEXT", 50, "Title"], 
             ["Url", "TEXT", 1024, "Url"], 
             ["InputRanges", "TEXT", 1024, "Input Ranges"], 
             ["OutputValues", "TEXT", 256, "Output Values"], 
             ["NoDataRanges", "TEXT", 256, "NoData Ranges"], 
             ["RangeLabels", "TEXT", 1024, "Range Labels"], 
             ["NoDataRangeLabels", "TEXT", 1024,"NoData Range Labels"]
          ]
agroRasters = []
# Read CSV file as list (CSV file stores information of rasters which are for creating mosaic)
# Alternative: Convert CSV file to JSON row array using https://github.com/shancarter/Mr-Data-Converter
print "Reading raster information from CSV file..."
with open(rasterTable, 'rb') as f:
    r = csv.reader(f)
    agroRasters = list(r)[1:]
f.close()

Rasters = []
for i in range(0,len(agroRasters)):
    Rasters.append(agroRasters[i][0])

arcpy.AddMessage("Creating mosaic dataset...") 

# Create Mosaic Dataset
try:
    if arcpy.Exists(agroMosaic):
        print agroMosaic, "exists, will be deleted"
        arcpy.DeleteMosaicDataset_management(agroMosaic)
        
    arcpy.CreateMosaicDataset_management(env.workspace, agroMosaic, Proj, "1", "32_BIT_SIGNED", "NONE", "")
    print "New mosaic dataset", agroMosaic, "was created\nAdding", len(agroRasters),"rasters to mosaic dataset..." 
    arcpy.AddRastersToMosaicDataset_management(agroMosaic, "Raster Dataset", Rasters, "UPDATE_CELL_SIZES", "UPDATE_BOUNDARY", "NO_OVERVIEWS", "", "0", "1500", Proj, "", "SUBFOLDERS", "OVERWRITE_DUPLICATES", "NO_PYRAMIDS", "CALCULATE_STATISTICS", "NO_THUMBNAILS", "", "NO_FORCE_SPATIAL_REFERENCE")
    arcpy.GetMessages()
    print "Caculating statistics..."
    arcpy.CalculateStatistics_management(agroMosaic, "1", "1", "", "SKIP_EXISTING")
except Exception as e:
    print e.message

arcpy.AddMessage("Adding required fields...") # Add required fields

for field in fields[1:]:
    # add 7 fields for Landscape Modeler web application
    arcpy.AddField_management(agroMosaic, field[0], field[1], "", "", field[2], field[3], "NULLABLE", "NON_REQUIRED", "")

arcpy.AddMessage("Analyzing mosaic dataset...") # Analyze mosaic dataset
try:
    arcpy.AnalyzeMosaicDataset_management(agroMosaic, "", "FOOTPRINT;FUNCTION;RASTER;PATHS;SOURCE_VALIDITY;STALE;PYRAMIDS;STATISTICS;PERFORMANCE;INFORMATION")
except Exception, e:
    print arcpy.GetMessages(messageCount - 1)

arcpy.AddMessage("Populating fields...") # Populate fields
popFields = [item[0] for i, item in enumerate(fields)]
print popFields
with arcpy.da.UpdateCursor(agroMosaic, popFields) as cursor:
    i = 0
    for row in cursor:
        # populate field only if the raster layer already exists in agroRasters
        if str(row[0]) == str(agroRasters[i][0]):
            cursor.updateRow(agroRasters[i])
            print "Updated:", agroRasters[i][1]                   
        else:
            print "Nothing was updated"
        i = i + 1
del cursor, row
print "Done."
