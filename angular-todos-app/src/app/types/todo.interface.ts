import { TodoStatus } from "./todo-status.enum";

export interface Todo {
  id: string,
  content: string;
  status: TodoStatus
}