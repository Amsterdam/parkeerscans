import { Component, ChangeDetectionStrategy } from '@angular/core';

@Component({
  selector: 'dp-map',
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './map.html',
  styleUrls: [
    './map.scss'
  ]
})
export class MapComponent {
}
