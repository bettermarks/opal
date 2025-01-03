# Hierarchy Provider Concept

The Hierarchy Provider (HP) is an API of an IDP / Group Management which provides the hierarchy the user is member of.
The HP API handlles 
* requests from authenticated users about the membership of the user
* requests from authenticated users about the hierarchy of the user

## Entities and Hierarchies

We call all elements of an hierarchy, entities. In the Example of the german school system this would look like this:

List of (possible) entities:
* ministry of education (Germany)
* ministry of education (federal state)
* school authority
* school
* grade level
* group (class / course)
* role (teacher / student / admin)

Those entities can be arranged in some 'natural' hierarchy,
e.g. some school has several classes, each of those classes has several students and
one (or maybe more) teachers. An entity is uniquely identified within the HP by some
identifier, we call it 'external identifier' (EID).

The Hierarchy Provider (HP) stores those entities and their hierarchical relations.

## The Hierarchy Provider
The HP is also an API, where authenticated users
or other services as Clients can get information about hierarchies of specific
entities. In order to fulfill the requirements for some environment including an LM,
the following routes must be implemented by an HP:

### Getting Hierarchy Levels
```
GET /hierarchy/levels
```
This route returns the hierarchy levels, that are used in the specific
hierarchy structure of the domain. Those hierarchy levels are used to
identify entities, which are associated with some given hierarchy level
(see below). A call to the route returns something like
```json
{
    "student": 0, 
    "teacher": 0, 
    "class": 1, 
    "school": 2,
    "school_authority": 3,
    "federal_state": 10,
}
```
There are two 'leaf levels' defined, 'teacher' and 'student' entity, a 'level 1'
entity named 'class' and a 'level 2' entity named 'school'. In this Example the grade level of a class is decided to be not part of the hierarchy.

### Getting all 'Memberships' for a Specific User
```
GET /hierarchy/users/{user EID}/membership
```
This route gets all the memberships of a given user including the user themselves and returns something like
```json
[
  {"type": "federal_state", "level": 10, "eid": "12"}, 
  {"type": "school_authority", "level": 3, "eid": "104258"},
  {"type": "school", "level": 2, "eid": "999"}, 
  {"type": "school", "level": 2, "eid": "888"},
  {"type": "class", "level": 1, "eid": "344"},
  {"type": "class", "level": 1, "eid": "566"},
  {"type": "teacher", "level": 0, "eid": "IDP::123"}
]
```
This means that a user 'IDP::123' (who is associated with a 
hierarchy level 'teacher') is currently member of a hierarchy level
named 'class' and has EID='344' and of some 'class' with EID='566',
which both are 'located' in some hierarchy level 'school' with EID='999'.
Additionally, 'teacher' 'IDP:123' is also member of school '888' the schools belong to 1 school authority (10428) and a federal state (12).

The hierarchy concept is not showing how the entities are linked to each other. Because this is not needed for our purpose yet. But of course this could be added later to the concept.