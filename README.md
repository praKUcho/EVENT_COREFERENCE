# EVENT_COREFERENCE PROJECT

parseECB.py

Use "python parseECB.py ECB+_path" command.
Produces 3 types of Outputs.
1- 1_all_files.txt which has sentences clustered based on event. 
e.g.- 
ACT15736700251185985  t1_treatment
Lohan , who has been in rehab a total of five times before this , was previously in Betty Ford in 2010 . 1_14ecbplus.xml
She's in rehab right now . 1_21ecbplus.xml
She  s in rehab right now . 1_5ecbplus.xml
2- out_tagged folder: Contains all words tagged with their tag descriptor and instance id. (each token is 2-tab separated)
e.g.- 
Lindsay__HUM15732980283919140__t1_lindsay_lohan		Lohan__HUM15732980283919140__t1_lindsay_lohan		Leaves__ACT15736206310398879__t1_leaving_betty_ford		Betty__LOC15734326865367655__t1_betty_ford		Ford__LOC15734326865367655__t1_betty_ford		,__NONE__NONE		Checks__ACT15986681471021312__t1_checking_into_cliffside		Into__ACT15986681471021312__t1_checking_into_cliffside		Malibu__LOC15737144640543698__t1_cliffside	
Rehab__LOC15737144640543698__t1_cliffside
3- out_text folder: Contains text for each article
Lindsay Lohan Leaves Betty Ford , Checks Into Malibu Rehab
