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

  removeTodo(id: string): void {
    const updatedTodos = this.todos$
      .getValue()
      .filter((todo) => todo.id !== id);
    this.todos$.next(updatedTodos);
  }

  toggleTodoStatus(id: string): void {
    const updatedTodos = this.todos$
      .getValue()
      .map((todo) => {
        if (todo.id == id) {
          let status;
          if (todo.status == TodoStatus.ACTIVE) {
            status = TodoStatus.COMPLETE;
          } else {
            status = TodoStatus.ACTIVE;
          }
          return {
            ...todo, status: status
          }
        }
        return todo;
      });
    this.todos$.next(updatedTodos);
  }

  changeFilter(filter: Filter) {
    this.filter$.next(filter);
  }
}