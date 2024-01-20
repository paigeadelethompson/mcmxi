# Quick start
 
- initialize the bot `mkdir /mcmxi ; docker run -it --rm -v /mcmxi:/home/mcmxi paigeadele/mcmxi install`
- create the configuration file (initial): `docker run -it --rm -v /mcmxi:/home/mcmxi paigeadele/mcmxi run mcmxi`
- edit the configuration file `/mcmxi/sopel.cfg`
- start the bot `docker run -it --restart always -d -v /mcmxi:/home/mcmxi paigeadele/mcmxi run mcmxi`
