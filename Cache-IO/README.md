## Input / Output System for Cache related exports. 

The main idea is to read an XML export from InterSystems HealthShare / Ensemble, that contains either a class or a production definition. The tool uses an XML SAX parser to parse the file and output a graph definition either in PlantUML or GraphML notation. As a result, we can generate nice looking class/component diagrams semi-autonomously by using this script instead of handwriting these diagrams.

Partial credit on how to use XML SAX parsers fetched from here: https://bitbucket.org/swcv/worldgenerator/

## Sample output
![alt text](https://user-images.githubusercontent.com/670459/46409159-285d9200-c71d-11e8-93e8-f8044c5c9e16.png)
