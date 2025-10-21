# pages/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import json
from django.db.models import Q
from django.core.paginator import Paginator

# Import your models
from .models import Profile, Message, Thread, Like, Block, PrivateAccessRequest

# Core Pages
def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'pages/home.html')

@login_required
def dashboard(request):
    # Your existing dashboard logic
    user_profile = Profile.objects.get(user=request.user)
    suggested_profiles = Profile.objects.filter(
        is_approved=True
    ).exclude(
        Q(user=request.user) |
        Q(user__in=Block.objects.filter(blocker=request.user).values('blocked')) |
        Q(user__in=Block.objects.filter(blocked=request.user).values('blocker'))
    )
    
    # Add pagination - 12 profiles per page
    paginator = Paginator(suggested_profiles, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'profile': user_profile,
        'suggested_profiles': page_obj,  # Now it's paginated
    }
    return render(request, 'pages/gr8date_dashboard_fixed_v10_nolines.html', context)

# Profile Management
@login_required
def profile_view(request):
    profile = Profile.objects.get(user=request.user)
    context = {'profile': profile}
    return render(request, 'pages/profile_view.html', context)

@login_required
def profile_edit(request):
    profile = Profile.objects.get(user=request.user)
    
    if request.method == 'POST':
        # Your existing profile edit logic
        profile.headline = request.POST.get('headline', '')
        profile.about = request.POST.get('about', '')
        profile.location = request.POST.get('location', '')
        profile.occupation = request.POST.get('occupation', '')
        profile.my_gender = request.POST.get('my_gender', '')
        profile.looking_for = request.POST.get('looking_for', '')
        profile.my_interests = request.POST.get('my_interests', '')
        profile.children = request.POST.get('children', '')
        profile.preferred_age_min = request.POST.get('preferred_age_min', 18)
        profile.preferred_age_max = request.POST.get('preferred_age_max', 99)
        profile.preferred_intent = request.POST.get('preferred_intent', '')
        profile.preferred_distance = request.POST.get('preferred_distance', '')
        profile.save()
        
        return redirect('profile_view')
    
    context = {'profile': profile}
    return render(request, 'pages/profile_edit.html', context)

@login_required
def profile_detail(request, user_id):
    profile = get_object_or_404(Profile, user_id=user_id)
    is_own_profile = request.user == profile.user
    
    # Check if requester has active access to private photos
    has_private_access = False
    access_request = None
    has_pending_request = False
    
    if not is_own_profile and request.user.is_authenticated:
        access_request = PrivateAccessRequest.objects.filter(
            requester=request.user,
            target_user=profile.user
        ).first()
        
        if access_request:
            if access_request.status == 'approved':
                has_private_access = True
            elif access_request.status == 'pending':
                has_pending_request = True
    
    # Get images
    public_images = profile.images.filter(is_private=False)
    private_images = profile.images.filter(is_private=True)
    
    # Your existing context variables
    is_liked = Like.objects.filter(
        liker=request.user, 
        liked_user=profile.user
    ).exists()
    
    is_blocked = Block.objects.filter(
        blocker=request.user,
        blocked=profile.user
    ).exists()
    
    # Get next/previous profiles for navigation
    all_profiles = Profile.objects.filter(is_approved=True).exclude(user=request.user)
    current_index = list(all_profiles).index(profile) if profile in list(all_profiles) else -1
    
    previous_profile_id = None
    next_profile_id = None
    
    if current_index > 0:
        previous_profile_id = all_profiles[current_index - 1].user_id
    if current_index < len(all_profiles) - 1:
        next_profile_id = all_profiles[current_index + 1].user_id
    
    context = {
        'profile': profile,
        'public_images': public_images,
        'private_images': private_images,
        'is_own_profile': is_own_profile,
        'has_private_access': has_private_access,
        'has_pending_request': has_pending_request,
        'access_request': access_request,
        'is_liked': is_liked,
        'is_blocked': is_blocked,
        'previous_profile_id': previous_profile_id,
        'next_profile_id': next_profile_id,
    }
    return render(request, 'pages/profile_view.html', context)

# Search & Discovery
@login_required
def search(request):
    query = request.GET.get('q', '')
    results = []
    
    if query:
        results = Profile.objects.filter(
            Q(user__username__icontains=query) |
            Q(headline__icontains=query) |
            Q(about__icontains=query) |
            Q(location__icontains=query) |
            Q(occupation__icontains=query) |
            Q(my_interests__icontains=query)
        ).exclude(user=request.user)
    
    context = {
        'query': query,
        'results': results,
    }
    return render(request, 'pages/search.html', context)

# Likes & Matching
@login_required
def like_user(request, user_id):
    if request.method == 'POST':
        target_user = get_object_or_404(User, id=user_id)
        
        like, created = Like.objects.get_or_create(
            liker=request.user,
            liked_user=target_user
        )
        
        if not created:
            like.delete()
            return JsonResponse({'status': 'unliked'})
        
        return JsonResponse({'status': 'liked'})
    
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def unfavorite_user(request, user_id):
    if request.method == 'POST':
        target_user = get_object_or_404(User, id=user_id)
        
        Like.objects.filter(
            liker=request.user,
            liked_user=target_user
        ).delete()
        
        return JsonResponse({'status': 'unfavorited'})
    
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def likes_received(request):
    likes = Like.objects.filter(
        liked_user=request.user
    ).select_related('liker', 'liker__profile')
    
    context = {'likes': likes}
    return render(request, 'pages/likes_received.html', context)

@login_required
def likes_given(request):
    likes = Like.objects.filter(
        liker=request.user
    ).select_related('liked_user', 'liked_user__profile')
    
    context = {'likes': likes}
    return render(request, 'pages/likes_given.html', context)

@login_required
def matches_list(request):
    # Get all likes given by current user
    likes_given = Like.objects.filter(
        liker=request.user
    ).select_related('liked_user', 'liked_user__profile')
    
    # Get all likes received by current user  
    likes_received = Like.objects.filter(
        liked_user=request.user
    ).select_related('liker', 'liker__profile')
    
    # Get all blocked users
    blocked_users = Block.objects.filter(
        blocker=request.user
    ).select_related('blocked', 'blocked__profile')
    
    context = {
        'likes_given': likes_given,
        'likes_received': likes_received, 
        'blocked_users': blocked_users
    }
    return render(request, 'pages/matches_list.html', context)

# Messaging
@login_required
def messages_combined(request):
    threads = Thread.objects.filter(
        Q(user_a=request.user) | Q(user_b=request.user)
    ).prefetch_related('messages').order_by('-updated_at')
    
    # ADD THIS: Calculate unread_count for each thread BEFORE marking as read
    for thread in threads:
        thread.unread_count = thread.messages.filter(
            recipient=request.user,
            is_read=False
        ).count()
        
    # Mark threads as read when user views them (keep this as is)
    for thread in threads:   
        thread.messages.filter(
            recipient=request.user,
            is_read=False
        ).update(is_read=True)

    # Get access requests for the current user
    pending_requests_received = PrivateAccessRequest.objects.filter(
        target_user=request.user,
        status='pending'
    )
            
    context = {
        'threads': threads,
        'pending_requests_received': pending_requests_received
    }   
    return render(request, 'pages/messages_combined.html', context)

@login_required
def message_thread(request, user_id):
    other_user = get_object_or_404(User, id=user_id)
    
    # Get or create thread
    thread = Thread.get_or_create_for(request.user, other_user)
    
    if request.method == 'POST':
        text = request.POST.get('text', '').strip()
        if text:
            Message.objects.create(
                thread=thread,
                sender=request.user,
                recipient=other_user,
                text=text
            )
            return JsonResponse({'success': True})
        return JsonResponse({'success': False, 'error': 'Empty message'})
    
    messages = thread.messages.all().order_by('created_at')
    
    context = {
        'thread': thread,
        'other_user': other_user,
        'messages': messages,
    }
    return render(request, 'pages/message_thread.html', context)

@login_required
def delete_conversation(request, thread_id):
    if request.method == 'POST':
        thread = get_object_or_404(Thread, id=thread_id)
        
        # Verify user is part of the thread
        if request.user not in [thread.user_a, thread.user_b]:
            return JsonResponse({'ok': False, 'error': 'Not authorized'})
        
        # Delete all messages in the thread
        thread.messages.all().delete()
        
        return JsonResponse({'ok': True})
    
    return JsonResponse({'ok': False, 'error': 'Invalid method'})

@login_required
def messages_unread_count(request):
    count = Message.objects.filter(
        recipient=request.user,
        is_read=False
    ).count()
    
    return JsonResponse({'count': count})

# Private Photo Access Views
@login_required
def request_private_access(request, user_id):
    if request.method == 'POST':
        target_user = get_object_or_404(User, id=user_id)
        
        # Don't allow requesting access to yourself
        if request.user == target_user:
            return JsonResponse({'status': 'error', 'message': 'Cannot request access to your own photos'})
        
        # Check if already exists
        existing_request = PrivateAccessRequest.objects.filter(
            requester=request.user,
            target_user=target_user
        ).first()
        
        if existing_request:
            if existing_request.status == 'pending':
                return JsonResponse({'status': 'pending', 'message': 'Request already pending'})
            elif existing_request.status == 'approved':
                return JsonResponse({'status': 'already_approved', 'message': 'You already have access'})
        
        # Create new request
        access_request = PrivateAccessRequest.objects.create(
            requester=request.user,
            target_user=target_user
        )
        
        # Send notification message to target user
        message_text = f"🔒 {request.user.username} requested access to your private photos. Go to your pending requests to approve or deny."
        Message.objects.create(
            thread=Thread.get_or_create_for(request.user, target_user),
            sender=request.user,
            recipient=target_user,
            text=message_text
        )
        
        return JsonResponse({'status': 'request_sent', 'message': 'Access request sent!'})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

@login_required
def approve_private_access(request, request_id):
    access_request = get_object_or_404(PrivateAccessRequest, id=request_id, target_user=request.user)
    
    if access_request.status == 'pending':
        access_request.status = 'approved'
        access_request.reviewed_by = request.user
        access_request.reviewed_at = timezone.now()
        access_request.save()  # This will automatically set expires_at
        
        # Send approval message with 72-hour notice
        approval_message = f"✅ {request.user.username} approved your private photo access request! You can now view their private photos for 72 hours."
        Message.objects.create(
            thread=Thread.get_or_create_for(request.user, access_request.requester),
            sender=request.user,
            recipient=access_request.requester,
            text=approval_message
        )
        
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'approved', 'message': 'Access granted for 72 hours!'})
        else:
            return redirect('messages_list')
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})

@login_required
def deny_private_access(request, request_id):
    access_request = get_object_or_404(PrivateAccessRequest, id=request_id, target_user=request.user)
    
    if access_request.status == 'pending':
        access_request.status = 'denied'
        access_request.reviewed_by = request.user
        access_request.reviewed_at = timezone.now()
        access_request.save()
        
        # Send denial message
        denial_message = f"❌ {request.user.username} denied your private photo access request."
        Message.objects.create(
            thread=Thread.get_or_create_for(request.user, access_request.requester),
            sender=request.user,
            recipient=access_request.requester,
            text=denial_message
        )
        
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'denied', 'message': 'Access denied'})
        else:
            return redirect('messages_list')
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})

@login_required
def pending_requests(request):
    # Get pending requests for the current user
    pending_requests = PrivateAccessRequest.objects.filter(
        target_user=request.user,
        status='pending'
    ).select_related('requester', 'requester__profile')
    
    context = {
        'pending_requests': pending_requests
    }
    return render(request, 'pages/pending_requests.html', context)

# Blog
def blog_list(request):
    # Your blog logic
    posts = []  # Replace with your actual blog posts query
    context = {'posts': posts}
    return render(request, 'pages/blog_list.html', context)

def blog_detail(request, slug):
    # Your blog detail logic
    post = None  # Replace with your actual blog post query
    context = {'post': post}
    return render(request, 'pages/blog_detail.html', context)

# Admin Approval System
@login_required
def admin_profile_approvals(request):
    if not request.user.is_staff:
        return redirect('dashboard')
    
    pending_profiles = Profile.objects.filter(is_approved=False)
    context = {'pending_profiles': pending_profiles}
    return render(request, 'pages/admin_approvals.html', context)

@login_required
def admin_approve_profile(request, profile_id):
    if not request.user.is_staff:
        return redirect('dashboard')
    
    profile = get_object_or_404(Profile, id=profile_id)
    profile.is_approved = True
    profile.save()
    
    return redirect('admin_profile_approvals')

@login_required
def admin_reject_profile(request, profile_id):
    if not request.user.is_staff:
        return redirect('dashboard')
    
    profile = get_object_or_404(Profile, id=profile_id)
    # You might want to add a reason field or delete the profile
    profile.delete()
    
    return redirect('admin_profile_approvals')

# Blocking
@login_required
def block_user(request, user_id):
    if request.method == 'POST':
        target_user = get_object_or_404(User, id=user_id)
        
        Block.objects.get_or_create(
            blocker=request.user,
            blocked=target_user
        )
        
        return redirect('profile_detail', user_id=user_id)
    
    return redirect('dashboard')

@login_required
def unblock_user(request, user_id):
    target_user = get_object_or_404(User, id=user_id)
    
    Block.objects.filter(
        blocker=request.user,
        blocked=target_user
    ).delete()
    
    return redirect('profile_detail', user_id=user_id)
