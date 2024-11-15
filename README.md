# SOEN342 Project

### Antoine Mansour (40250454) Section H
### Sadee Mohammad Shadman (40236919) Scetion H    

---

#### Use Case UML:    

![Use Case UML](Use%20Case%20UML.png)      


#### Domain Model:

![Domain Model](DomainModel.png)  

#### Class Diagram:

![Domain Model](ClassDiagram.png)  


#### Package Diagram:

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

**Operation**: `login(username, password)`    
**Cross reference**: Use Case Process Offerings, Use Case Process Bookings

- **Preconditions**:  
  - The credentials must exist in the system.

- **Postconditions**:  
  - If valid, the `setRole` method sets the role of the user as either an `admin`, `instructor` or `client`.
  - If valid, the user with the role is authenticated into the system
  - If invalid, an error message is shown.

---

#### 2. `create_location`

**Operation**: `create_location(city, address, location)`    
**Cross reference**: Use Case Process Offerings

- **Preconditions**:  
  - The `Administrator` is logged in.
  - The `location` details must include valid detals.
  
- **Postconditions**:  
  - If the `location` is unique (checked by `checkLocationUniqueness()`) with valid details, the system creates the new offering.
  - If the `location` is not unique or has invalid details, the system returns an error message.

---     

#### 3. `checkLocationUniqueness`

**Operation**: `checkLocationUniqueness()`    
**Cross reference**: Use Case Process Offerings

- **Preconditions**:  
  - The system has received a valid location submission from the `administrator`.

- **Postconditions**:  
  - The system confirms that no location already exists at the same city, name, and address.
  - If no conflict is found, it proceeds to confirm the creation.
  - If a conflict is found, it returns an error message to the `administrator`.
 
--- 

#### 4. `create_offering`

**Operation**: `create_offering(lessonType, offeringType, startTime, endTime, date, maxCapacity)`    
**Cross reference**: Use Case Process Offerings

- **Preconditions**:  
  - The `Administrator` is logged in.
  - The `offering` details must include valid detals.
  
- **Postconditions**:  
  - If the `offering` is unique (checked by `checkOfferingUniqueness`) with valid details, the system creates the new offering.
  - If the `offering` is not unique or has invalid details, the system returns an error message.

---     

#### 5. `checkOfferingUniqueness`

**Operation**: `checkOfferingUniqueness()`    
**Cross reference**: Use Case Process Offerings

- **Preconditions**:  
  - The system has received a valid offering submission from the `administrator`.

- **Postconditions**:  
  - The system confirms that no offering already exists at the same location, date, and time slot.
  - If no conflict is found, it proceeds to confirm the creation.
  - If a conflict is found, it returns an error message to the `administrator`.

---

#### 6. `diaplayUnassignedOfferings`

**Operation**: `diaplayUnassignedOfferings()`     
**Cross reference**: Use Case Process Offerings

- **Preconditions**:  
  - The `admin` or `Instructor` is authenticated and logged in.

- **Postconditions**:  
  - If there exists, the system returns a list of all available `offerings` (those that have not been claimed by an instructor).
  - If there are no unassigned `offerings`, an empty page is shown.

---

#### 7. `claim_offering`

**Operation**: `claim_offering(offering_id)`     
**Cross reference**: Use Case Process Offerings

- **Preconditions**:  
  - The `Instructor` is authenticated and logged in.
  - The `offering` must be available (found by `diaplayUnassignedOfferings()`).
  - The `offering` city and lessonType must match the `Instructor` city and speciality that they are available to work in.

- **Postconditions**:  
  - The selected `offering` is now associated with the `instructor`.
  - The `offering` is removed from the list of unassigned offerings`.
  - The `offering` is now public and anyone can see it or attend it.

---       

#### 8. `displayOfferings`

**Operation**: `dispplayOfferings()`     
**Cross reference**: Use Case Process Offerings, Process Bookings

- **Preconditions**:  
  - An `offering` has been claimed by an instructor. 

- **Postconditions**:  
  - The list of `offerings` claimed by instructors are displayed to the user (guest or registered).

---

#### 9. `attend_offering`

**Operation**: `attend_offering(offering_id)`     
**Cross reference**: Use Case Process Bookings

- **Preconditions**:  
  - The `Client` is authenticated and logged in.
  - The `Client` has selected the person to book the offering for (themselves or a child that they will accompany)
  - The `offering` must have available capacity.
  - The `offering`'s startTime and endTime must not conflict with another scheduled booking of the `Client`. 

- **Postconditions**:  
  - The selected `offering` is now booked by the `Client`.
  - The `offering` is now displayed with a capacity 1 less than before.
  - The `offering` and its details are now available under `bookings` of the `Client`.

---

Interaction Diagram of Create Location (Admin):

![Communication Diagram of Create Location](Communication%20Diagram%20Create%20Location.PNG)    
   
     
Interaction Diagram of Create Offering (Admin):

![Communication Diagram of Create Offering](Communication%20Diagram%20Create%20Offering.PNG)      


Interaction Diagram of Book (Client):

![Communication Diagram of Book](Communication%20Diagram%20Book.PNG)   


Interaction Diagram of Accept Offering (Instructor):

![Communication Diagram of Create Location](Communication%20Diagram%20Accept%20Offering.PNG)       

   
Interaction Diagram of Remove Attendee (Admin):

![Communication Diagram of Remove Attendee](Communication%20Diagram%20Remove%20Attendee.PNG)      


Interaction Diagram of Register (Guest User):

![Communication Diagram of Register](Communication%20Diagram%20Register.PNG)   
  

Relational Data Model:
 ![Relational Data Model](RelationalDataModel.png) 


#### Requirement 1:   
“Offerings are unique. In other words, multiple offerings on the same day and time slot must be offered at a different location.”

```
context Offering
inv UniqueOfferingsByLocation:
    Offering.allInstances()->forAll(o1, o2 |
        o1 <> o2 implies
        (o1.start_time <> o2.start_time or o1.end_time <> o2.end_time or o1.date <> o2.date or o1.location_id <> o2.location_id)
    )
```
#### Requirement 2:   
“Any client who is underage must necessarily be accompanied by an adult who acts as their guardian.”
```
context Booking
inv UnderageBooking:
    -- Ensure that only adult clients (age >= 18) can make a booking
    self.client.age >= 18
```
#### Requirement 3:  
“The city associated with an offering must be one the city’s that the instructor has indicated in their availabilities.”

```
context Offering
inv CityMatchesInstructorAvailability:
    let offeringCity : String = self.location.city in
        Instructor.allInstances()->exists(instructor |
            instructor.id = self.instructor_id and
            instructor.city = offeringCity)

```
#### Requirement 4:
“A client does not have multiple bookings on the same day and time slot.” (for simplicity we consider only identical day and time slots, even though in reality a booking on Monday 3pm – 4pm and another also on Monday 3:30pm – 4:30pm should not be acceptable.)
```
context Booking
inv NoMultipleBookingsForSameClientAndTime:
    Booking.allInstances()->forAll(b1, b2 |
        b1 <> b2 implies
        (b1.client_id <> b2.client_id or b1.start_time <> b2.start_time or b1.end_time <> b2.end_time or b1.date <> b2.date)
    )
```

