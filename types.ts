
export enum Theme {
    Light = 'light',
    Dark = 'dark',
}

export interface Member {
    id: string;
    name: string;
    monthlyAttendance: number;
    quarterlyAttendance: number;
}

export interface Signup {
    id: string;
    name: string;
    type: 'member' | 'guest';
    timestamp: Date;
}

export interface GameSession {
    id: string;
    date: Date;
    signups: Signup[];
}

export interface Deadlines {
    registrationOpens: Date;
    registrationCloses: Date;
    guestRegistrationOpens: Date;
    cancellationDeadline: Date;
}
