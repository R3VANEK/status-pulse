## User roles

Application uses RBAC policy with permissions stored in DB.
Possible roles are either `Student` or `Supervisor`.
They are project-scoped, meaning user can be supervisor in project A and student in project B

| Permission/Role               | Student | Supervisor |
| ----------------------------- | ------- | ---------- |
| adding new project            | [v]     | [v]        |
| deleting project              | [x]     | [v]        |
| modifying project             | [x]     | [v]        |
| adding new persons to project | [x]     | [v]        |
| adding new task               | [v]     | [v]        |
| editing task                  | [v]     | [v]        |
| completing task               | [x]     | [v]        |
| adding attachments to task    | [v]     | [v]        |
| adding attachments to project | [v]     | [v]        |
| chat                          | [v]     | [v]        |
