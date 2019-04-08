import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { QuesComponent } from './ques.component';

describe('QuesComponent', () => {
  let component: QuesComponent;
  let fixture: ComponentFixture<QuesComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ QuesComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(QuesComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
