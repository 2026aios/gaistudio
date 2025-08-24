import { Member } from './types';

export const INITIAL_MEMBERS: Member[] = [
    { id: 'm01', name: '黃老師', monthlyAttendance: 0, quarterlyAttendance: 0 },
    { id: 'm02', name: '阿平', monthlyAttendance: 0, quarterlyAttendance: 0 },
    { id: 'm03', name: '我', monthlyAttendance: 0, quarterlyAttendance: 0 },
    { id: 'm04', name: '皮', monthlyAttendance: 0, quarterlyAttendance: 0 },
    { id: 'm05', name: '張清文', monthlyAttendance: 0, quarterlyAttendance: 0 },
    { id: 'm06', name: '文姿', monthlyAttendance: 0, quarterlyAttendance: 0 },
    { id: 'm07', name: '智宇', monthlyAttendance: 0, quarterlyAttendance: 0 },
    { id: 'm08', name: '克拉克', monthlyAttendance: 0, quarterlyAttendance: 0 },
    { id: 'm09', name: 'Ben', monthlyAttendance: 0, quarterlyAttendance: 0 },
    { id: 'm10', name: '雄', monthlyAttendance: 0, quarterlyAttendance: 0 },
    { id: 'm11', name: '明正', monthlyAttendance: 0, quarterlyAttendance: 0 },
    { id: 'm12', name: '曜竹', monthlyAttendance: 0, quarterlyAttendance: 0 },
    { id: 'm13', name: '阿生', monthlyAttendance: 0, quarterlyAttendance: 0 },
    { id: 'm14', name: '哲維', monthlyAttendance: 0, quarterlyAttendance: 0 },
    { id: 'm15', name: '查理王', monthlyAttendance: 0, quarterlyAttendance: 0 },
    { id: 'm16', name: '🦅', monthlyAttendance: 0, quarterlyAttendance: 0 },
    { id: 'm17', name: '怡姍', monthlyAttendance: 0, quarterlyAttendance: 0 },
    { id: 'm18', name: '控', monthlyAttendance: 0, quarterlyAttendance: 0 },
    { id: 'm19', name: '彥皓', monthlyAttendance: 0, quarterlyAttendance: 0 },
    { id: 'm20', name: '海哥', monthlyAttendance: 0, quarterlyAttendance: 0 },
    { id: 'm21', name: '阿嘉', monthlyAttendance: 0, quarterlyAttendance: 0 },
    { id: 'm22', name: '許', monthlyAttendance: 0, quarterlyAttendance: 0 },
];

// 0 = Sunday, 1 = Monday, ..., 6 = Saturday
export const GAME_DAYS_OF_WEEK: number[] = [1, 3, 5]; // Monday, Wednesday, Friday
export const GAME_HOUR = 9; // 9 AM
export const GAME_MINUTE = 0;


export const GUEST_REGISTRATION_PLAYER_THRESHOLD = 17;

export const QUARTERLY_FEE_BASE = 2500;
export const QUARTERLY_FEE_THRESHOLD = 25;
export const QUARTERLY_FEE_PER_GAME_EXTRA = 100;