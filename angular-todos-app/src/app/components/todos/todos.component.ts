import { Component } from '@angular/core';
import { HeaderComponent } from '../header/header.component';

@Component({
  selector: 'app-todos',
  standalone: true,
  imports: [HeaderComponent],
  templateUrl: './todos.component.html'
})
export class TodosComponent {
  title = 'todos';
}
