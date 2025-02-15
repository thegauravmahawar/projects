import { Component, EventEmitter, Input, OnChanges, OnInit, Output } from '@angular/core';
import { HeaderComponent } from '../header/header.component';
import { Todo } from '../../types/todo.interface';
import { TodoService } from './todos.service';

@Component({
  selector: 'app-todos',
  standalone: true,
  imports: [HeaderComponent],
  providers: [TodoService],
  templateUrl: './todos.component.html'
})
export class TodosComponent {

  @Input('todo') todo: Todo;

  constructor(private todoService: TodoService) {}

  toggleTodoStatus(): void {
    console.log('Change todo status');
    this.todoService.toggleTodoStatus(this.todo.id);
  }

  removeTodo(): void {
    console.log('Remove todo');
    this.todoService.removeTodo(this.todo.id);
  }

}
