if ! [ $1 ];
then
    echo "Usage: ./move-urls-to-resources.sh <directory>"
    exit 1
fi

if ! [ -d $1 ];
then
    echo "Parameter must be a directory"
    exit 1
fi

sed -i "s/<dc:date>\(https:\/\/www\.wikidata\.org\/wiki\/Q[0-9]*\)<\/dc:date>/<dc:date rdf:resource=\"\1\"\/>/" $1/*.xml

sed -i "s/<dcterms:spatial>\(https:\/\/www\.wikidata\.org\/wiki\/Q[0-9]*\)<\/dcterms:spatial>/<dcterms:spatial rdf:resource=\"\1\"\/>/" $1/*.xml

sed -i "s/<dcterms:spatial>\(http:\/\/www\.geonames\.org\/[0-9]*\)<\/dcterms:spatial>/<dcterms:spatial rdf:resource=\"\1\"\/>/" $1/*.xml

sed -i "s/<dc:type xml:lang=\"eng\">\(http:\/\/vocab\.getty\.edu\/page\/aat\/[0-9]*\)<\/dc:type>/<dc:type rdf:resource=\"\1\"\/>/" $1/*.xml

