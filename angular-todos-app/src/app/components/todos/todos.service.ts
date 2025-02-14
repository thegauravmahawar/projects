import { BehaviorSubject } from "rxjs";
import { TodoStatus } from "../../types/todo-status.enum";
import { Todo } from "../../types/todo.interface";
import { Filter } from "../../types/filter.enum";

export class TodoService {

  todos$ = new BehaviorSubject<Todo[]>([]);
  filter$ = new BehaviorSubject<Filter>(Filter.ALL);

  createTodo(todo: string): void {
    const newTodo: Todo = {
      todo,
      status: TodoStatus.ACTIVE,
      id: Math.random().toString(16)
    }
    const updatedTodos = [...this.todos$.getValue(), newTodo];
    this.todos$.next(updatedTodos);
  }
}