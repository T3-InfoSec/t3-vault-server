### Documentation: T3 Vault Server - Database Structure and State Flow

---

### **1. Overview**

T3 Vault Server is a task management platform that facilitates secure communication and task processing between **clients** and **solvers**. The system uses WebSocket connections to manage real-time communication, enforce rate limits, and assign tasks. The server employs encryption for secure data transmission and maintains a well-defined database schema to handle task flow effectively.

---

### **2. Database Structure**

#### **Core Tables**
1. **Clients Table**  
   Tracks information about clients who request tasks.
   - **Fields**:
     - `client_id`: Unique identifier (fingerprint).
     - `tasks_requested`: Number of tasks requested by the client.

2. **Solvers Table**  
   Tracks solver metadata and reputation.
   - **Fields**:
     - `solver_id`: Unique identifier (fingerprint).
     - `db_key`: Primary key.
     - `is_online`: Boolean, indicates whether the solver is online.
     - `reputation_score`: Numeric, indicates the solver's reputation.
     - `tasks_taken`: Number of tasks assigned to this solver.

3. **Tasks Table**  
   Represents tasks created by clients.
   - **Fields**:
     - `fingerprint`: Unique task identifier.
     - `client_id`: Foreign key linking to the client.
     - `parameter_t`, `parameter_baseg`, `parameter_product`: Task-specific parameters (encrypted).
     - `difficulty`: Computed difficulty of the task.
     - `first_assignment_id`, `second_assignment_id`: Foreign keys linking to task assignments.
     - `num_assignments`: Number of times the task has been assigned.

4. **TaskAssignments Table**  
   Links tasks to solvers, recording task-specific assignments.
   - **Fields**:
     - `task_id`: Foreign key linking to the task fingerprint.
     - `solver_id`: Foreign key linking to the solver.
     - `task_key`: Task's database key.
     - `deadline`: Task completion deadline.
     - `complaint_deadline`: Deadline for complaints.
     - `db_key`: Unique identifier for the task assignment.

---

### **3. State Flow**

#### **3.1 Client Task Creation**
1. **Trigger**: A client sends a task creation request.
2. **Steps**:
   - Parameters (`t`, `baseg`, `product`) are encrypted and stored.
   - The difficulty of the task is calculated.
   - The task is inserted into the `Tasks` table.
   - The `tasks_requested` field for the client is incremented.
3. **State**: Task is stored and ready for assignment.

---

#### **3.2 Task Assignment to Solvers**
1. **Trigger**: A new task is created or a solver comes online.
2. **Steps**:
   - A solver is queried based on availability (`is_online=1`) and reputation.
   - A `TaskAssignment` record is created:
     - Links the task to the solver.
     - Assigns deadlines (`deadline`, `complaint_deadline`).
   - The task's assignment metadata (`first_assignment_id`, `second_assignment_id`) is updated.
   - The solver's `tasks_taken` field is incremented.
3. **State**: Task is assigned and awaiting processing.

---

#### **3.3 Solver Task Processing**
1. **Trigger**: Solver receives task assignment via WebSocket.
2. **Steps**:
   - Task parameters (`t`, `baseg`, `product`) are decrypted.
   - The solver processes the task and submits results.
   - Results are validated.
3. **State**: Task processing is completed, or complaints are raised.

---

#### **3.4 Rate Limiting and Solver Reputation**
1. **Rate Limiting**:
   - Solvers are tracked for the number of requests in a `RATE_LIMIT_WINDOW`.
   - Exceeding `MAX_REQUESTS_PER_WINDOW` bans the solver temporarily (`BAN_DURATION`).
   - Repeated violations reduce solver reputation (`reduce_solver_reputation`).
2. **Reputation Handling**:
   - Reputation is adjusted based on task performance and rate-limiting violations.
   - Banned solvers are tracked in a temporary ban list.

---

### **4. WebSocket Connections**

#### **4.1 Client WebSocket**
- Handles messages from clients, including task creation (`TLP`) and complaints.
- Routes messages based on `MessageType`:
  - `TLP`: Triggers task creation (`handle_tlp_task_creation`).
  - `COMPLAINT`: Routes to appropriate handlers for dispute resolution.

#### **4.2 Solver WebSocket**
- Handles solver task assignment and rate-limiting.
- Routes messages based on `MessageSolverResponseType`:
  - `TLP_RESPONSE`: Processes solver responses.
  - `PING`: Maintains active connection status.

---

### **5. Task Assignment Events**

#### **Event Listener: `on_task_assignment_insert`**
- Triggered after a task is assigned to a solver.
- Retrieves the solver and task details.
- Initiates task handling via `handle_tlp_task_assignment_assign_to_solver`.

---

### **6. Encryption**
- **Library**: `Encryption`
- Usage:
  - **Client Data**: Encrypted using the client's fingerprint as the key.
  - **Solver Data**: Decrypted using the solver's fingerprint.
- Secure transmission ensures privacy and integrity.

---

### **7. Task Difficulty**
- **Formula**:  
  \[
  \text{Difficulty} = \frac{\lfloor \log_2(\text{product}) + 1 \rfloor}{t}
  \]
- Higher difficulty implies greater computational effort.

---

### **8. Error Handling**
1. **Unhandled Message Types**:
   - Logs a warning for unsupported message types.
2. **Invalid Messages**:
   - Ensures message integrity before processing.

---

### **9. Logs and Debugging**
- Logs include:
  - WebSocket connection events.
  - Task assignments and solver interactions.
  - Rate-limiting actions and solver bans.

---

This documentation provides an in-depth look at the database schema and state flow for the T3 Vault server. Each step is designed to ensure task management, data integrity, and system reliability.