import { TodoStatus } from "./todo-status.enum";

export interface Todo {
  id: string,
  todo: string;
  status: TodoStatus
}