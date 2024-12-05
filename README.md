# Shelved
This was kinda cool the one time it worked and then it was a terrible use of poetry 

# Quick start
 
- initialize the bot `mkdir /mcmxi ; chmod -R 777 /mcmxi ; docker run -it --rm -v /mcmxi:/home/mcmxi paigeadele/mcmxi install`
- create the configuration file (initial): `docker run -it --rm -v /mcmxi:/home/mcmxi paigeadele/mcmxi run mcmxi`
- edit the configuration file `/mcmxi/sopel.cfg`
- start the bot `docker run -it --restart always -d -v /mcmxi:/home/mcmxi paigeadele/mcmxi run mcmxi`
