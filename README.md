# SOEN342 Project

### Antoine Mansour (40250454) Section H
### Sadee Mohammad Shadman (40236919) Scetion H    

---

Use Case UML:    

![Use Case UML](./USE%20CASE%20UML.jpg)      


Domain Model:

![Domain Model](Domain%20Model.PNG)        


Package Diagram:

![Package Diagram](Package%20Dragram.PNG)     


System Sequence Diagram of Administrator (Create Offering):

![System Sequence Admin Scenario](SSD%20Admin%20Create%20Offering.PNG)         


System Sequence Diagram of Instructors (Accpet Offerings):

![System Sequence Instructor Scenario](SSD%20Instrcutor%20Accept%20Offerings.PNG)      


System Sequence Diagram of Clients (create Booking):

![System Sequence Client Scenario](SSD%20Client%20Create%20Booking.PNG)          

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

#### 2. `createNewOffering`

**Operation**: `createNewOffering(offeringDetails)`    
**Cross reference**: Use Case Process Offerings

- **Preconditions**:  
  - The `Administrator` is logged in.
  - The `offering` details must include valid location, schedule and lessonType.
  
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





