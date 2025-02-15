import { Component } from '@angular/core';
import { TodoService } from '../todos/todos.service';

@Component({
  selector: 'app-header',
  standalone: true,
  imports: [],
  providers: [TodoService],
  templateUrl: './header.component.html'
})
export class HeaderComponent {

  todo: string = '';

  constructor(private todoService: TodoService) {
  }

  changeTodo(event: Event): void {
    const target = event.target as HTMLInputElement;
    this.todo = target.value;
  }

  createTodo(): void {
    this.todoService.createTodo(this.todo);
  }
}