/**
 * Face Recognition Attendance System - Static Version
 * Powered by face-api.js and localStorage
 */

const APP_STORAGE_KEY = 'face_recognition_attendance_data';
const MODELS_URL = 'static/models'; // Local path, will fallback to CDN if needed

class FaceAttendanceApp {
    constructor() {
        this.users = [];
        this.attendance = [];
        this.loadData();
    }

    loadData() {
        const data = JSON.parse(localStorage.getItem(APP_STORAGE_KEY) || '{"users":[], "attendance":[]}');
        this.users = data.users.map(u => ({
            ...u,
            // Reconstruct the Float32Array from the stored array
            descriptors: u.descriptors.map(d => new Float32Array(Object.values(d)))
        }));
        this.attendance = data.attendance;
    }

    saveData() {
        localStorage.setItem(APP_STORAGE_KEY, JSON.stringify({
            users: this.users,
            attendance: this.attendance
        }));
    }

    async initModels() {
        try {
            console.log("Loading models...");
            // Use local models if available, otherwise fallback to CDN
            try {
                await Promise.all([
                    faceapi.nets.ssdMobilenetv1.loadFromUri(MODELS_URL),
                    faceapi.nets.faceLandmark68Net.loadFromUri(MODELS_URL),
                    faceapi.nets.faceRecognitionNet.loadFromUri(MODELS_URL)
                ]);
            } catch (e) {
                console.warn("Local models failed, trying CDN...", e);
                const CDN_URL = 'https://raw.githubusercontent.com/justadudewhohacks/face-api.js-models/master';
                await Promise.all([
                    faceapi.nets.ssdMobilenetv1.loadFromUri(CDN_URL),
                    faceapi.nets.faceLandmark68Net.loadFromUri(CDN_URL),
                    faceapi.nets.faceRecognitionNet.loadFromUri(CDN_URL)
                ]);
            }
            console.log("Models loaded successfully");
            return true;
        } catch (err) {
            console.error("Error loading models:", err);
            return false;
        }
    }

    async registerUser(name, studentId, descriptors) {
        // Check if user already exists
        if (this.users.some(u => u.studentId === studentId)) {
            throw new Error("User with this ID already exists.");
        }

        this.users.push({
            name,
            studentId,
            descriptors: descriptors.map(d => Array.from(d)), // Convert to array for storage
            createdAt: new Date().toISOString()
        });
        this.saveData();
        return true;
    }

    markAttendance(user) {
        const today = new Date().toISOString().split('T')[0];
        const alreadyMarked = this.attendance.some(a => a.studentId === user.studentId && a.date === today);

        if (!alreadyMarked) {
            const record = {
                studentId: user.studentId,
                name: user.name,
                date: today,
                time: new Date().toLocaleTimeString(),
                status: 'Present'
            };
            this.attendance.push(record);
            this.saveData();
            return { success: true, record };
        }
        return { success: false, message: "Already marked today" };
    }

    getStats() {
        const today = new Date().toISOString().split('T')[0];
        const todayAttendance = this.attendance.filter(a => a.date === today).length;
        return {
            totalUsers: this.users.length,
            todayAttendance,
            recentUsers: [...this.users].sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt)).slice(0, 5)
        };
    }

    getHistory() {
        return [...this.attendance].sort((a, b) => {
            const dateA = new Date(`${a.date} ${a.time}`);
            const dateB = new Date(`${b.date} ${b.time}`);
            return dateB - dateA;
        });
    }
}

const app = new FaceAttendanceApp();
window.FaceApp = app; // Export for global access
