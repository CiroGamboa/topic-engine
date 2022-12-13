# topic-engine

#TODO: Make an introduction of the hackathon context, of Metaculus and the team members
with proper links

1. Use docker to build and run a local neo4j instance using the following command:

docker run \
  --name testneo4j \
  -p7474:7474 -p7687:7687 \
  -d \
  -v $HOME/neo4j/data:/data \
  -v $HOME/neo4j/logs:/logs \
  -v $HOME/neo4j/import:/var/lib/neo4j/import \
  -v $HOME/neo4j/plugins:/plugins \
  --env NEO4J_AUTH=neo4j/test \
  neo4j:latest

The port 7474 is used for the web interface of the Neo4j client and the 7687 is used for API calls. A default database is created and the root user is neo4j, with password test


2. Topic extraction module

3. Merge datasets

4. Create nodes

5. Create relationships

6. Query the data


