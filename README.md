# SOEN342 Project

### Antoine Mansour (40250454) Section H
### Sadee Mohammad Shadman (40236919) Scetion H    

---

Use Case UML:    

![Use Case UML](./USE%20CASE%20UML.jpg)      


Domain Model:

![Domain Model](DomainModel.png)  

Class Diagram:

![Domain Model](ClassDiagram.png)  


Package Diagram:

![Package Diagram](Package%20Diagram.PNG)     


System Sequence Diagram of Administrator:

![System Sequence Admin Scenario](SSD%20Admin.PNG)         


System Sequence Diagram of Instructors:

![System Sequence Instructor Scenario](SSD%20Instructor.PNG)      


System Sequence Diagram of Clients:

![System Sequence Client Scenario](SSD%20Client.PNG)          

---    


### Operation Contracts


#### 1. `login`

**Operation**: `login(adminCredentials)`    
**Cross reference**: Use Case Process Offerings

- **Preconditions**:  
  - The `Administrator’s` credentials must exist in the system.

- **Postconditions**:  
  - If valid, the `Administrator` is authenticated and logged in.
  - If invalid, an error message is shown.

---

#### 2. `createOffering`

**Operation**: `createOffering()`    
**Cross reference**: Use Case Process Offerings

- **Preconditions**:  
  - The `Administrator` is logged in.
  - The `offering` details must include valid detals.
  
- **Postconditions**:  
  - If the `offering` is unique (checked by `checkOfferingUniqueness`), the system creates the new offering.
  - If the `offering` is not unique, the system returns an error message.

---     

#### 3. `checkOfferingUniqueness`

**Operation**: `checkOfferingUniqueness(offeringDetails)`    
**Cross reference**: Use Case Process Offerings

- **Preconditions**:  
  - The system has received a valid offering submission from the `administrator`.

- **Postconditions**:  
  - The system confirms that no offering already exists at the same location, date, and time slot.
  - If no conflict is found, it proceeds to confirm the creation.
  - If a conflict is found, it returns an error message to the `administrator`.

---

#### 4. `viewAvailableOfferings`

**Operation**: `viewAvailableOfferings()`     
**Cross reference**: Use Case Process Offerings

- **Preconditions**:  
  - The `Instructor` is authenticated and logged in.

- **Postconditions**:  
  - The system returns a list of all available `offerings` (those that have not been selected by other instructors).

---

#### 5. `selectOffering`

**Operation**: `selectOffering(offeringId)`     
**Cross reference**: Use Case Process Offerings

- **Preconditions**:  
  - The `Instructor` is authenticated and logged in.
  - The `offering` must be available (not yet selected by another instructor).

- **Postconditions**:  
  - The selected `offering` is now associated with the `instructor`.
  - The `offering` is marked as unavailable for other `instructors`.

--- 

Interaction Diagram of Create Location (Admin):

![Communication Diagram of Create Location](Communication%20Diagram%20Create%20Location.PNG)    
   
     
Interaction Diagram of Create Offering (Admin):

![Communication Diagram of Create Offering](Communication%20Diagram%20Create%20Offering.PNG)      


Interaction Diagram of Book (Client):

![Communication Diagram of Book](Communication%20Diagram%20Book.PNG)   


Interaction Diagram of Accept Offering (Instructor):

![Communication Diagram of Create Location](Communication%20Diagram%20Accept%20Offering.PNG) 
  

Relational Data Model:
 ![Relational Data Model](RelationalDataModel.png) 


